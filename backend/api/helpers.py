from api.models import Server
from django.contrib.auth.models import User


def can_manage_server(server: Server, user: User) -> bool:
    """Checks if user with user_id can manage given server

    Args:
        user (django.contrib.auth.models.user): ID of the user that should be checked for permission to access server
        server (api.models.Server): server instance that should be checked
    Returns:
        bool: Whether or not the given user is allowed to access the given server.
    """

    if user.is_superuser or user.is_staff:
        return True

    allowed_users = []
    for u in server.allowed_users.all():
        allowed_users.append(u)

    return user in allowed_users
