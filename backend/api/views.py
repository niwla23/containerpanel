from django.http import JsonResponse, HttpRequest
from channels.http import AsgiRequest


def is_authenticated(request: AsgiRequest) -> JsonResponse:
    """Checks if request is authenticated.

    Useful for checking if user needs to be redirected to OIDC provider.

    Args:
        request (AsgiRequest): The incoming request

    Returns:
        JsonResponse: JSON response with the key "is_authenticated" showing whether or not request was authenticated.

    """

    return JsonResponse({"is_authenticated": request.user.is_authenticated})
