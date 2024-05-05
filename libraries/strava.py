from dataclasses import dataclass, fields
from datetime import datetime
from enum import Enum
from urllib.parse import urlencode, urljoin
from typing import List, Optional, TYPE_CHECKING

import httpx
from dateutil import parser

from django.conf import settings
from django.utils import timezone
from django.urls import reverse

from tracker.apps.users.models import User, StravaProfile
from tracker.apps.activities.models import Activity
from tracker.core.constants import MeasurementUnit

if TYPE_CHECKING:
    from tracker.apps.shoes.models import Shoes


TIMEOUT = 10
BASE_URL = 'https://www.strava.com/api/v3/'
STRAVA_SPORT_TYPES = {
    'Run': Activity.Type.RUN,
    'VirtualRun': Activity.Type.RUN,
    'TrailRun': Activity.Type.TRAIL,
    'Walk': Activity.Type.WALK,
}


class GrantType(Enum):
    AUTHORIZATION_CODE = 'authorization_code'
    REFRESH_TOKEN = 'refresh_token'


@dataclass
class StravaActivity:
    id: str
    name: str
    distance: float
    moving_time: int
    type: str
    created: datetime
    shoes_id: str
    shoes: Optional['Shoes'] = None

    @property
    def converted_distance(self) -> float:
        return round(self.distance / 1000, 1)


@dataclass
class StravaShoes:
    id: str
    name: str
    nickname: str
    retired: bool
    distance: int
    converted_distance: float


class StravaException(Exception):
    pass


def get_headers(user: User) -> dict:
    token = get_access_token(user)
    return {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }


def get_authorization_url(user: User) -> str:
    query_params = {
        'client_id': settings.STRAVA_CLIENT_ID,
        'redirect_uri': urljoin(settings.HOST_URL, reverse('api:strava:authorized')),
        'response_type': 'code',
        'approval_prompt': 'auto',
        'scope': 'read,profile:read_all,activity:read_all',
        'state': user.id,
    }
    return 'https://www.strava.com/oauth/authorize?' + urlencode(query_params)


def authorize_user(user: User, code: str, commit: bool = False) -> StravaProfile:
    response = _get_access_token(code, GrantType.AUTHORIZATION_CODE)
    response.raise_for_status()

    data = response.json()
    profile = getattr(user, 'strava_profile', StravaProfile(user=user))
    profile.athlete_id = data['athlete']['id']
    profile.access_token = data['access_token']
    profile.refresh_token = data['refresh_token']
    profile.expires_at = data['expires_at']
    if data['athlete']['measurement_preference'] == 'meters':
        user.measurement_unit = MeasurementUnit.METRIC
    else:
        user.measurement_unit = MeasurementUnit.MILES

    if commit:
        profile.save()
        user.save(update_fields=['measurement_unit'])

    return profile


def get_access_token(user: User) -> str:
    profile = user.strava_profile
    current_ts = int(timezone.now().timestamp())

    # Refresh token if it expires within 5 minutes
    if current_ts > (profile.expires_at - 300):
        response = _get_access_token(profile.refresh_token, GrantType.REFRESH_TOKEN)
        response.raise_for_status()
        data = response.json()
        profile.access_token = data['access_token']
        profile.refresh_token = data['refresh_token']
        profile.expires_at = data['expires_at']
        profile.save(update_fields=['access_token', 'refresh_token', 'expires_at'])

    return profile.access_token


def _get_access_token(token: str, grant_type: GrantType) -> httpx.Response:
    url = 'https://www.strava.com/api/v3/oauth/token'
    data = {
        'client_id': settings.STRAVA_CLIENT_ID,
        'client_secret': settings.STRAVA_CLIENT_SECRET,
        'refresh_token': token,
        'grant_type': grant_type.value,
    }

    if grant_type == GrantType.REFRESH_TOKEN:
        data['refresh_token'] = token
    elif grant_type == GrantType.AUTHORIZATION_CODE:
        data['code'] = token

    return httpx.post(url=url, json=data, timeout=TIMEOUT)


def get_athlete_shoes(user: User) -> List[StravaShoes]:
    response = get_athlete_profile(user)
    response.raise_for_status()
    data = response.json()
    shoes_attributes = {field.name for field in fields(StravaShoes)}
    result = []
    for shoes_data in data['shoes']:
        attributes = {key: value for key, value in shoes_data.items() if key in shoes_attributes}
        result.append(StravaShoes(**attributes))

    return result


def get_athlete_profile(user: User) -> httpx.Response:
    url = BASE_URL + 'athlete'
    headers = get_headers(user)
    return httpx.get(url=url, headers=headers, timeout=TIMEOUT)


def get_gear_detail(shoes: 'Shoes') -> httpx.Response:
    if not shoes.strava_id:
        raise ValueError(f'Shoes {shoes} have no strava ID')

    headers = get_headers(shoes.user)
    url = BASE_URL + f'gear/{shoes.strava_id}'
    return httpx.get(url=url, headers=headers, timeout=TIMEOUT)


def get_athlete_activities(user: User, after: datetime) -> httpx.Response:
    response = get_activities(user, after)
    response.raise_for_status()

    data = response.json()
    activity_attributes = {field.name for field in fields(StravaActivity)}
    result = []
    for activity_data in data:
        attributes = {key: value for key, value in activity_data.items() if key in activity_attributes}
        attributes.update({
            'created': parser.parse(activity_data['start_date']),
            'shoes_id': activity_data['gear_id'],
        })
        activity = StravaActivity(**attributes)
        if STRAVA_SPORT_TYPES.get(activity.type):
            result.append(activity)

    # Reverse to sort activities by descending time
    return result[::-1]


def get_activities(user: User, after: datetime) -> httpx.Response:
    headers = get_headers(user)
    url = BASE_URL + 'activities'
    query = {
        'after': int(after.timestamp()),
    }
    return httpx.get(url=url, params=query, headers=headers, timeout=TIMEOUT)


def get_activity_detail(activity_id: str, user: User) -> httpx.Response:
    headers = get_headers(user)
    url = BASE_URL + f'activities/{activity_id}'
    return httpx.get(url=url, headers=headers, timeout=TIMEOUT)


def create_webhook_subscription() -> httpx.Response:
    url = BASE_URL + 'push_subscriptions'
    data = {
        'client_id': settings.STRAVA_CLIENT_ID,
        'client_secret': settings.STRAVA_CLIENT_SECRET,
        'callback_url': urljoin(settings.HOST_URL, reverse('api:strava:notification')),
        'verify_token': settings.STRAVA_VERIFY_TOKEN,
    }
    return httpx.post(url=url, json=data, timeout=TIMEOUT)


def view_webhook_subscription() -> httpx.Response:
    url = BASE_URL + 'push_subscriptions'
    data = {
        'client_id': settings.STRAVA_CLIENT_ID,
        'client_secret': settings.STRAVA_CLIENT_SECRET,
    }
    return httpx.get(url=url, params=data, timeout=TIMEOUT)


def delete_webhook_subscription(subscription_id: str) -> httpx.Response:
    url = BASE_URL + f'push_subscriptions/{subscription_id}'
    data = {
        'client_id': settings.STRAVA_CLIENT_ID,
        'client_secret': settings.STRAVA_CLIENT_SECRET,
    }
    return httpx.delete(url, params=data, timeout=TIMEOUT)
