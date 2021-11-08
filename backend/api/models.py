import os
import secrets
import subprocess
import time
from typing import List, Tuple, Dict, Any

import django.template
import docker
import yaml
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from docker.errors import NotFound
from dateutil.parser import isoparse


def create_id() -> str:
    """creates an id to identify a server.

    Returns:
        str: 5 digit hex id
    """

    return secrets.token_hex(5)


class Server(models.Model):
    server_id = models.CharField(primary_key=True, default=create_id, editable=False, max_length=5, unique=True)
    description = models.CharField(max_length=200)
    name = models.CharField(max_length=200, unique=True)
    command_prefix = models.CharField(max_length=400)
    allowed_users = models.ManyToManyField(User, verbose_name="Users allowed to manage this server")
    template = models.CharField(max_length=100)
    port = models.IntegerField(unique=True)
    sftp_port = models.IntegerField(unique=True)
    sftp_password = models.CharField(max_length=64)
    max_cpu_usage = models.FloatField()
    max_memory_usage = models.FloatField()
    host = models.CharField(default=settings.SERVER_DEFAULT_HOST, max_length=255)

    docker_client = None
    container = None
    container_available = True

    def load_docker_client(self):
        """loads the docker client.

        Loads the docker client instance into the class variable `docker_client` if it is not loaded yet.
        """
        if not self.docker_client:
            self.docker_client = docker.from_env()

    def load_container(self):
        """loads the container object.

        Loads the main docker container related to this server into the class variable `container`
        If the container was not found, it sets the class variable `container_available` to `False` and
        `container` to None
        If class variable docker_client is `None`, it loads the docker client using `self.load_docker_client()`
        """

        if not self.docker_client:
            self.load_docker_client()
        if not self.container:
            try:
                self.container = self.docker_client.containers.get(str(self.name) + "_main_1")
            except NotFound:
                self.container_available = False
                self.container = None

    def create(self, template_config: Dict[str, str]):
        """Creates the Docker containers belonging to this server.

        This function should be called after populating a new instance of `Server` with data and saving it.
        It renders the template given with the values given to the `Server` instance.
        Then it creates a directory with the servers `name` and creates
        docker-compose file with the rendered template.
        In the end it runs `docker-compose up -d` to bring up the project.
        """

        self.load_docker_client()
        with open(f"app_templates.v2/{self.template}.yml", "r") as file:
            template_string = file.read()
            template = django.template.Template(template_string)
            context = django.template.Context({
                "name": self.name,
                "description": self.description,
                "port": self.port,
                "sftp_port": self.sftp_port,
                "sftp_password": self.sftp_password,
                "max_cpu_usage": self.max_cpu_usage,
                "max_memory_usage": self.max_memory_usage,
                "template_config": template_config,
                "timezone": os.environ["TIMEZONE"]
            })

            config = yaml.safe_load(template.render(context))
            compose_config = yaml.safe_dump(config["compose_config"], sort_keys=False)

            self.command_prefix = config["command_prefix"]

            path = f"{os.environ['APP_DIR']}/{self.name}"

            if os.path.exists(path):
                raise FileExistsError("path is not empty")

            subprocess.Popen(["mkdir", "-p", path]).wait()
            with open(f"{os.environ['APP_DIR']}/{self.name}/docker-compose.yml", "w") as compose_file:
                compose_file.write(compose_config)
            subprocess.Popen(["docker-compose", "up", "-d"], cwd=path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).wait()

    def power_action(self, action: str):
        """Performs a power action for the server

        Executes a power event on the main container connected to this server.

        Args:
            action (str): The action to perform. One of "start", "stop", "restart" or "kill"

        Raises:
            ValueError: action was not in list of supported power actions.
        """

        self.load_container()
        if action == "stop":
            self.container.stop()
        elif action == "kill":
            self.container.kill()
        elif action == "start":
            self.container.start()
        elif action == "restart":
            self.container.restart()
        else:
            raise ValueError("action must be 'start', 'stop', 'restart' or 'kill'.")

    @property
    def running(self):
        """Defines whether or not the server is running

        Returns:
            bool: `True` means server is running, `False` means it is not.
        """

        self.load_container()
        if self.container_available:
            return self.container.status == "running"
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

    def get_logs(self, lines: int) -> List[Dict]:
        """Returns the last log lines as list of strings.

        Args:
            lines (int): Number of lines to return

        Returns:
            list: List of log lines
        """

        self.load_container()
        if self.container_available:
            logs = self.container.logs(tail=lines, timestamps=True).decode().split("\n")
            logs_formatted = []
            for line in logs:
                try:
                    split = line.split(" ")
                    timestamp = time.mktime(isoparse(split[0]).timetuple())
                    logs_formatted.append({"timestamp": timestamp, "content": ' '.join(split[1:]), "source": "log"})
                except ValueError:
                    pass
            return logs_formatted
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
        print(self.command_prefix)
        result = self.container.exec_run(str(self.command_prefix) + " " + command)
        return result.exit_code, result.output.decode()

    def is_user_allowed_to_manage(self, user: User) -> bool:
        """Checks if user with user_id can manage given server

        Args:
            user (django.contrib.auth.models.user): ID of the user that should be checked for permission to access server
        Returns:
            bool: Whether or not the given user is allowed to access the given server.
        """

        if user.is_superuser or user.is_staff:
            return True

        allowed_users = []
        for u in self.allowed_users.all():
            allowed_users.append(u)

        return user in allowed_users

    def __repr__(self):
        """Defines how the class should be printed.

        Returns:
            str: human-readable name of the server
        """

        return self.description

    def __str__(self):
        """Defines how the class should be converted to a string.

        Returns:
            str: human-readable name of the server
        """

        return self.description
