import os
import random
import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import SESSION_KEY
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
import docker
import yaml
from .models import Container
from .forms import PowerActionForm, CreateContainerForm, get_create_container_form, patch_form_with_users
from .helpers import can_manage_container, format_env
from django.conf import settings
import socketio
from datetime import datetime, timedelta
import subprocess

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
                      {"containers": containers, "profile_url": settings.OIDC_PROFILE_URL})
    else:
        return redirect("oidc_authentication_init")


@login_required
def add_choose(request):
    return render(request, 'panel/add_choose.html')


@login_required
def choose_template(request):
    app_template_dir = "app_templates"
    files = os.listdir(app_template_dir)
    templates = {}
    for file in files:
        if file.endswith(".yml"):
            with open(f"{app_template_dir}/{file}") as stream:
                template = yaml.load(stream, Loader=yaml.FullLoader)
                templates[file[:-4]] = template["config"]
    return render(request, 'panel/choose_template.html', {"templates": templates})


@login_required
def add_new(request):
    if request.method == "GET":
        form = get_create_container_form()
    elif request.method == "POST":
        form = patch_form_with_users(CreateContainerForm(request.POST))
        print(form)
        if form.is_valid():
            print("yay")

            stack_name = form.cleaned_data["name"]
            description = form.cleaned_data["description"]
            image = form.cleaned_data["image"]
            environment = form.cleaned_data["env"].split(";")
            volumes = form.cleaned_data["volumes"].split(";")
            ports = form.cleaned_data["ports"].split(";")
            user_ids = form.cleaned_data["users"]
            command_prefix = form.cleaned_data["command_prefix"]

            path = f"{os.environ['APP_DIR']}/{stack_name}"
            subprocess.call(["mkdir", "-p", path])

            environment_as_dict = {}
            for variable in environment:
                environment_as_dict[variable.split("=")[0].strip()] = variable.split("=")[1].strip()

            config = {
                "version": "3",
                "services": {
                    "main": {
                        "image": image,
                        "ports": ports,
                        "volumes": volumes,
                        "environment": environment_as_dict,
                        "restart": "unless-stopped",
                    }
                }
            }
            with open(f"{os.environ['APP_DIR']}/{stack_name}/docker-compose.yml", "w") as compose_file:
                compose_file.write(yaml.dump(config, sort_keys=False))
            subprocess.Popen(["docker-compose", "up", "-d"], cwd=path)
            new_container = Container()
            new_container.name = f"{stack_name}_main_1"
            new_container.description = description
            new_container.command_prefix = command_prefix
            new_container.save()
            new_container.allowed_users.add(request.user)
            for user_id in user_ids:
                user = User.objects.get(id=int(user_id))
                print(user)
                new_container.allowed_users.add(user)
            new_container.save()
            return redirect("container", new_container.container_id)

    return render(request, 'panel/add_new.html', {"form": form})


@login_required
def template_add(request, template_name):
    with open(f"app_templates/{template_name}.yml", "r") as file:
        template = yaml.load(file)
    print(template)
    config = template["config"]
    form = get_create_container_form(initial={
        "image": config["image"],
        "env": format_env(config["env"]),
        "volumes": ";".join(config["volumes"]),
        "ports": ";".join(config["ports"]).replace("<port>", str(random.randint(11111, 65534))),
        "command_prefix": template["command_prefix"]
    })

    return render(request, 'panel/add_new.html', {"form": form})


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
            try:
                cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage'][
                    'total_usage']
                system_cpu_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
                data['cpu'] = round((cpu_delta / system_cpu_delta) * stats['cpu_stats']['online_cpus'] * 100, 2)
                data['memory'] = round(
                    (stats['memory_stats']['usage'] - stats['memory_stats']['stats']['cache']) / 1000000000, 2)
            except KeyError:
                pass

        # logs
        since_date = datetime.now() - timedelta(minutes=15)
        data["logs"] = current_container.logs(follow=False, since=since_date, stream=False).decode().split("\n")[:500]
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


def get_user_id_socketio(cookie):
    session = Session.objects.get(session_key=cookie)
    session_data = session.get_decoded()
    _throw_away = session_data[SESSION_KEY]
    return session_data.get('_auth_user_id')


@sio.event
def i_want_logs(sid, message):
    try:
        uid = get_user_id_socketio(message['cookie'])
        user: User = User.objects.get(id=uid)
        db_data = get_object_or_404(Container, pk=message["container_id"])
        if can_manage_container(db_data, user.id):
            client = docker.from_env()
            current_container = client.containers.get(db_data.name)
            for line in current_container.logs(stream=True, follow=True, since=datetime.now()):
                sio.emit("logs", {'line': line.decode('utf-8')}, room=sid)

    except (Session.DoesNotExist, KeyError):
        pass


@sio.event
def command(sid, message):
    uid = get_user_id_socketio(message['cookie'])
    user: User = User.objects.get(id=uid)
    db_data = get_object_or_404(Container, pk=message["container_id"])
    if can_manage_container(db_data, user.id):
        sio.emit("logs", {'line': "> " + message['command'], 'type': 'input'}, room=sid)
        client = docker.from_env()
        current_container = client.containers.get(db_data.name)
        print(db_data.command_prefix)
        response = current_container.exec_run(db_data.command_prefix + " " + message["command"])
        sio.emit("logs", {'line': response.output.decode(), 'type': 'response'}, room=sid)
