# crowdfund_project/middleware.py

from django.http import HttpResponse

class ALBHealthCheckBypassMiddleware:
    """
    Allow ALB / ECS health check to bypass Host validation
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # ALB health check path
        if request.path == "/health/":
            return HttpResponse("ok", status=200)

        return self.get_response(request)
