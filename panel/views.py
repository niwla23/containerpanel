import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import SESSION_KEY
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
import docker
import json
from .models import Container
from .forms import PowerActionForm
from .helpers import can_manage_container
from django.conf import settings
import socketio
from datetime import datetime
sio = socketio.Server(cors_allowed_origins=settings.ALLOWED_HOSTS)


def login(request):
    return redirect("oidc_authentication_init")


@login_required
def index(request):
    if request.user.is_authenticated:
        containers = []
        for i in Container.objects.order_by('description'):
            allowed_users = []
            for j in i.allowed_users.all():
                allowed_users.append(j.id)

            if request.user.id in allowed_users:
                containers.append({"id": str(i.container_id), "description": i.description})
        return render(request, 'panel/index.html',
                      {"containers": containers, "profile_url": settings.OIDC_PROFILE_URL })
    else:
        return redirect("oidc_authentication_init")


@login_required
def container(request, container_id):
    db_data = get_object_or_404(Container, pk=container_id)
    if can_manage_container(db_data, request.user.id):
        client = docker.from_env()
        current_container = client.containers.get(db_data.name)

        data = {
            "profile_url": settings.OIDC_PROFILE_URL,
            "description": db_data.description,
            "container_id": db_data.container_id,
            "state": current_container.status,
            "allowed_users": db_data.allowed_users.all(),
            "cpu": 0,
            'memory': 0
        }
        if current_container.status == "running":
            stats = current_container.stats(stream=False)
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage'][
                'total_usage']
            system_cpu_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
            data['cpu'] = round((cpu_delta / system_cpu_delta) * stats['cpu_stats']['online_cpus'] * 100, 2)
            data['memory'] = round(
                (stats['memory_stats']['usage'] - stats['memory_stats']['stats']['cache']) / 1000000000, 2)
        return render(request, 'panel/container.html', data)
    else:
        return redirect("index")


@login_required
def power_action(request, container_id):
    if request.method == "POST":
        form = PowerActionForm(request.POST)
        if form.is_valid():
            db_data = get_object_or_404(Container, pk=container_id)
            if can_manage_container(db_data, request.user.id):
                try:
                    client = docker.from_env()
                    action = form.cleaned_data["action"]
                    current_container = client.containers.get(db_data.name)
                    if action == "stop":
                        current_container.stop()
                    elif action == "kill":
                        current_container.kill()
                    elif action == "start":
                        current_container.start()
                    elif action == "restart":
                        current_container.restart()
                except docker.errors.APIError:
                    pass
            else:
                return redirect("index")

        return redirect("container", container_id)


@sio.event
def i_want_logs(sid, message):
    print("cookie", message['cookie'])
    try:
        session = Session.objects.get(session_key=message['cookie'])
        session_data = session.get_decoded()
        _throw_away = session_data[SESSION_KEY]
        uid = session_data.get('_auth_user_id')
        user: User = User.objects.get(id=uid)
        db_data = get_object_or_404(Container, pk=message["container_id"])
        if can_manage_container(db_data, user.id):
            client = docker.from_env()
            current_container = client.containers.get(db_data.name)
            for line in current_container.logs(stream=True, follow=True, since=datetime.now()):
                sio.emit("logs", {'line': line.decode('utf-8')}, room=sid)
                sio.sleep(0.01)

    except (Session.DoesNotExist, KeyError):
        pass


