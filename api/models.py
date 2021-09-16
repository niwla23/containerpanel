import os
import subprocess

from django.db import models
from django.contrib.auth.models import User
import django.template
import secrets
import yaml
import docker


def create_id():
    return secrets.token_hex(5)


class Server(models.Model):
    server_id = models.CharField(primary_key=True, default=create_id, editable=False, max_length=5)
    description = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    command_prefix = models.CharField(max_length=400)
    allowed_users = models.ManyToManyField(User, verbose_name="Users allowed to manage this server")
    template = models.CharField(max_length=100)
    port = models.IntegerField()
    sftp_port = models.IntegerField()
    sftp_password = models.CharField(max_length=64)
    max_cpu_usage = models.FloatField()
    max_memory_usage = models.FloatField()

    docker_client = None
    container = None

    def load_docker_client(self):
        if not self.docker_client:
            self.docker_client = docker.from_env()

    def load_container(self):
        if not self.docker_client:
            self.load_docker_client()
        if not self.container:
            self.container = self.docker_client.containers.get(self.name + "_main_1")

    def create(self):
        self.load_docker_client()
        template_config = {
            "mc_version": "1.17",
            "force_redownload": "0"
        }
        with open(f"app_templates.v2/{self.template}.yml", "r") as file:
            template_string = file.read()
            template = django.template.Template(template_string)
            print(self.max_memory_usage)
            context = django.template.Context({
                "name": self.name,
                "description": self.description,
                "port": self.port,
                "sftp_port": self.sftp_port,
                "sftp_password": self.sftp_password,
                "max_cpu_usage": self.max_cpu_usage,
                "max_memory_usage": self.max_memory_usage,
                "template_config": template_config
            })
            compose_config = yaml.safe_dump(yaml.safe_load(template.render(context))["compose_config"], sort_keys=False)

            path = f"{os.environ['APP_DIR']}/{self.name}"
            subprocess.call(["mkdir", "-p", path])
            with open(f"{os.environ['APP_DIR']}/{self.name}/docker-compose.yml", "w") as compose_file:
                compose_file.write(compose_config)
            subprocess.Popen(["docker-compose", "up", "-d"], cwd=path)

    def power_action(self, action: str):
        self.load_container()
        if action == "stop":
            self.container.stop()
        elif action == "kill":
            self.container.kill()
        elif action == "start":
            print("starting")
            self.container.start()
            print("started")
        elif action == "restart":
            self.container.restart()
        else:
            raise ValueError("action must be 'start', 'stop', 'restart' or 'kill'.")

    @property
    def running(self):
        self.load_container()
        return self.container.status == "running"

    @property
    def stats(self):
        self.load_container()
        stats = self.container.stats(stream=False)

        if self.running:
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage'][
                'total_usage']
            system_cpu_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
            cpu_usage = (cpu_delta / system_cpu_delta) * stats['cpu_stats']['online_cpus']
            memory_usage = stats['memory_stats']['usage']

            return cpu_usage, memory_usage
        return 0, 0

    def __repr__(self):
        return self.description

    def __str__(self):
        return self.description
