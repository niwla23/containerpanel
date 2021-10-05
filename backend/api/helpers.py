from api.models import Server


def can_manage_server(server: Server, user_id: int):
    """Checks if user with user_id can manage given server

    Args:
        user_id (int): ID of the user that should be checked for permission to access server
        server (Server): server instance that should be checked
    """
    allowed_users = []
    for j in server.allowed_users.all():
        allowed_users.append(j.id)

    return user_id in allowed_users


def format_env(env: dict) -> str:
    """Formats a dict of environment variables into a string.

    Args:
        env (dict): Mapping of environment variable names and their values. Ex.: {"VERSION": "1.12"}

    Returns:
        str: The formatted environment string
    """
    result = ""
    for (key, val) in env.items():
        result = result + "; " + str(key) + "=" + str(val)
    result = result[1:]
    return result
