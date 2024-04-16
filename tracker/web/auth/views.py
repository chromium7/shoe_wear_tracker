from django.http import HttpRequest, HttpResponse


def dummy(request: HttpRequest) -> HttpResponse:
    return HttpResponse('hello world')
