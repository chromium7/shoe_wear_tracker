from typing import TYPE_CHECKING

import httpx

from django_redis import get_redis_connection
from django.conf import settings

if TYPE_CHECKING:
    from tracker.apps.activities.models import Activity
    from tracker.apps.users.models import User


TIMEOUT = 10
BASE_URL = 'https://www.strava.com/api/v3/'
ACCESS_TOKEN_KEY = 'strava:access-token'
REFRESH_TOKEN_KEY = 'strava:refresh-token'


def get_headers() -> dict:
    token = get_access_token()
    return {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }


def get_access_token() -> str:
    redis = get_redis_connection()
    access_token = redis.get(ACCESS_TOKEN_KEY)
    if not access_token:
        refresh_token = redis.get(refresh_token)
        response = refresh_access_token(refresh_token)
        response.raise_for_status()

        data = response.json()
        access_token = data['access_token']
        expires_in = data['expires_in']
        refresh_token = data['refresh_token']
        redis.set(ACCESS_TOKEN_KEY, access_token, ex=(expires_in - 300))
        redis.set(REFRESH_TOKEN_KEY, refresh_token)

    return access_token


def refresh_access_token(refresh_token: str) -> httpx.Response:
    url = 'https://www.strava.com/api/v3/oauth/token'
    data = {
        'client_id': settings.STRAVA_CLIENT_ID,
        'client_secret': settings.STRAVA_CLIENT_SECRET,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
    }

    return httpx.post(url=url, json=data, timeout=TIMEOUT)


def get_gears(user: 'User') -> httpx.Response:
    if not user.strava_id:
        raise ValueError(f'User {user} has no strava ID')

    headers = get_headers()
    url = BASE_URL + f'gear/{user.strava_id}'
    return httpx.get(url=url, headers=headers, timeout=TIMEOUT)


def get_activity(activity: 'Activity') -> httpx.Response:
    if not activity.strava_id:
        raise ValueError(f'Activity {activity} has no strava ID')

    headers = get_headers()
    url = BASE_URL + f'activities/{activity.strava_id}'
    return httpx.get(url=url, headers=headers, timeout=TIMEOUT)
