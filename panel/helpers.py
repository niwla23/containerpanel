def can_manage_container(container, user_id):
    allowed_users = []
    for j in container.allowed_users.all():
        allowed_users.append(j.id)

    return user_id in allowed_users


def format_env(env):
    result = ""
    for (key, val) in env.items():
        result = result + "; " + str(key) + "=" + str(val)
    result = result[1:]
    return result
