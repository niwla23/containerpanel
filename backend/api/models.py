import os
import subprocess
from datetime import datetime
from typing import List, Tuple

from django.db import models
from django.contrib.auth.models import User
import django.template
import secrets
import yaml
import docker
from django.conf import settings
from docker.errors import NotFound


def create_id() -> str:
    """creates an id to identify a server.

    Returns:
        str: 5 digit hex id
    """

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
    host = models.CharField(default=settings.SERVER_DEFAULT_HOST, max_length=255)

    docker_client = None
    container = None
    container_available = True

    def load_docker_client(self):
        if not self.docker_client:
            self.docker_client = docker.from_env()

    def load_container(self):
        if not self.docker_client:
            self.load_docker_client()
        if not self.container:
            try:
                self.container = self.docker_client.containers.get(str(self.name) + "_main_1")
            except NotFound:
                self.container_available = False

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
            subprocess.Popen(["mkdir", "-p", path]).wait()
            with open(f"{os.environ['APP_DIR']}/{self.name}/docker-compose.yml", "w") as compose_file:
                compose_file.write(compose_config)
            subprocess.Popen(["docker-compose", "up", "-d"], cwd=path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).wait()

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
        if self.container_available:
            return self.container.status == "running"
        else:
            return False

    @property
    def stats(self):
        """Gets the cpu and memory usage of a server using docker api.

        Returns:
            int: cpu_usage
            int: memory_usage

        """
        self.load_container()

        if self.running:
            stats = self.container.stats(stream=False)
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage'][
                'total_usage']
            system_cpu_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
            cpu_usage = (cpu_delta / system_cpu_delta) * stats['cpu_stats']['online_cpus']
            memory_usage = stats['memory_stats']['usage']

            return cpu_usage, memory_usage
        return 0, 0

    def get_logs(self, lines: int) -> List[str]:
        """Returns the last log lines as list of strings.

        Args:
            lines (int): Number of lines to return

        Returns:
            list: List of log lines
        """

        self.load_container()
        if self.container_available:
            logs = self.container.logs(tail=lines, timestamps=True).decode().split("\n")
            return logs
        else:
            return []

    def exec_command(self, command: str) -> Tuple[int, str]:
        """Executes a command on the server

        Args:
            command (str): The command to execute. It will be prefixed with the command_prefix defined by the template

        Returns:
            tuple: A tuple of the return code (int) and the output (str)

        Raises:
            docker.errors.NotFound: the container for this server could not be found
        """
        self.load_container()
        result = self.container.exec_run(str(self.command_prefix) + " " + command)
        return result.exit_code, result.output.decode()

    def __repr__(self):
        return self.description

    def __str__(self):
        return self.description