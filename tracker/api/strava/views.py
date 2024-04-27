from rest_framework.request import Request
from rest_framework.response import Response

from django.shortcuts import redirect

from tracker.api.views import BaseAPIView
from tracker.api.response import ErrorResponse

from .forms import AuthorizationForm


class Notification(BaseAPIView):

    def get(self, request: Request) -> Response:
        pass


class Authorized(BaseAPIView):
    def get(self, request: Request) -> Response:
        form = AuthorizationForm(data=request.query_params)
        if not form.is_valid():
            return ErrorResponse(form)

        form.save()
        print('SUCCESS AUTHOIRZING SRATVA')

        return redirect('web:activities:index')
