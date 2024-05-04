from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from django.conf import settings
from django.shortcuts import redirect

from tracker.api.views import BaseAPIView
from tracker.api.response import ErrorResponse

from .forms import AuthorizationForm, NotificationForm


class Notification(BaseAPIView):
    def get(self, request: Request) -> Response:
        mode = request.query_params.get('hub.mode')
        token = request.query_params.get('hub.verify_token')
        challenge = request.query_params.get('hub.challenge')
        if mode and token:
            if mode == 'subscribe' and token == settings.STRAVA_VERIFY_TOKEN:
                return Response(data={'hub.challenge': challenge})

        return Response(status=status.HTTP_403_FORBIDDEN)

    def post(self, request: Request) -> Response:
        form = NotificationForm(data=request.query_params)
        if not form.is_valid():
            # Must return 200 to acknowledge webhook
            return ErrorResponse(form=form, status=status.HTTP_200_OK)

        activity = form.save()
        data = {
            'status': 'ok',
            'activity': activity.id if activity else None,
        }
        return Response(data=data, status=status.HTTP_200_OK)


class Authorized(BaseAPIView):
    def get(self, request: Request) -> Response:
        form = AuthorizationForm(data=request.query_params)
        if not form.is_valid():
            return ErrorResponse(form)

        form.save()

        return redirect('web:activities:index')
