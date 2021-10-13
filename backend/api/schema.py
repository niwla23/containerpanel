import base64
import os
import re
import secrets
from typing import Dict, List

import graphene
import yaml
from django.contrib.auth.models import User
from graphene_django import DjangoObjectType

from api.models import Server


class ServerStateType(graphene.ObjectType):
    """Represents the State (running, cpu and memory) in graphql"""

    running = graphene.Boolean()
    cpu_usage = graphene.Float()
    memory_usage = graphene.Float()


class ServerType(DjangoObjectType):
    state = graphene.Field(ServerStateType)
    logs = graphene.List(graphene.String)

    def resolve_state(self, _info):
        server = Server.objects.get(pk=self.server_id)
        cpu_usage, memory_usage = server.stats
        return {
            "running": server.running,
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage
        }

    def resolve_logs(self, _info):
        server = Server.objects.get(pk=self.server_id)
        return server.get_logs(50)

    class Meta:
        model = Server
        fields = ("server_id", "description", "name", "command_prefix", "allowed_users", "port", "sftp_port", "host")


class TemplateType(graphene.ObjectType):
    """Represents an app templates in graphql"""

    name = graphene.String()
    title = graphene.String()
    description = graphene.String()


class UserType(DjangoObjectType):
    """Represents a django user in graphql"""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "id")


class ServerStateMutation(graphene.Mutation):
    """Mutates the state of a server.

    The desired state is defined by the action argument.
    action can be "start", "stop" or "restart".
    After receiving a state mutation it will keep the request on hold until the server reached the desired state.
    Once the state is correct, the selected fields of the server model are sent back.
    """

    class Arguments:
        server_id = graphene.ID()
        action = graphene.String()

    server = graphene.Field(ServerType)

    @classmethod
    def mutate(cls, _root, _info, server_id, action):
        server = Server.objects.get(pk=server_id)
        server.power_action(action)
        return ServerStateMutation(server=server)


class ExecCommandMutation(graphene.Mutation):
    """ Executes a command on the Server.

    This will only work if commands are enabled for the server.
    Commands are simple strings that are executed in the docker container with
    the command_prefix of the server prefixed.
    """

    class Arguments:
        server_id = graphene.ID()
        command = graphene.String()

    response = graphene.String()
    code = graphene.Int()

    @classmethod
    def mutate(cls, _root, _info, server_id, command):
        server = Server.objects.get(pk=server_id)
        code, output = server.exec_command(command)
        return ExecCommandMutation(response=output, code=code)


class TemplateOptions(graphene.InputObjectType):
    """Represents the template specific options. Ex.: server version, game mode

    Args:
        key (graphene.String): Key for the template option. Ex.: VERSION
        value (graphene.String): Value for the template option. Ex.: 1.17.1
    """
    key = graphene.String()
    value = graphene.String()


class CreateServerMutation(graphene.Mutation):
    """Creates a new server.

    Args:
        name (str): Technical name of the container. This may only consist of lowercase letters, numbers and underscores
        description (str): Human readable version of the container name.
        template (str): Name of the template to use when creating this server.
        options (list): List of special options for the template. Ex.: Server version
        port (int): The port on which the game server listens (on host network)
        sftp_port (int): The port for the SFTP server (on host network)
        allowed_users (list): List of user ids allowed to manage the server

    """

    class Arguments:
        name = graphene.String()
        description = graphene.String()
        template = graphene.String()
        options = graphene.List(TemplateOptions)
        port = graphene.Int()
        sftp_port = graphene.Int()
        allowed_users = graphene.List(graphene.ID)

    server = graphene.Field(ServerType)

    @classmethod
    def mutate(cls, _root, _info, name: str, description: str, template: str, options: List[TemplateOptions], port: int, sftp_port: int,
               allowed_users: list):

        if port > 60000 or port < 1000:
            raise ValueError("port number must be between 1000 and 60000")

        if sftp_port > 60000 or sftp_port < 1000:
            raise ValueError("port number must be between 1000 and 60000")

        if not re.match("^[a-z0-9_]+$", name):
            raise ValueError("server name may only contain lowercase letters, numbers and underscores")

        # todo: check if port is used

        options_dict = {}
        for option in options:
            options_dict[str(option.key)] = str(option.value)

        server = Server()
        server.name = name
        server.description = description
        server.template = template
        server.port = port
        server.sftp_port = sftp_port
        server.sftp_password = base64.b64encode(secrets.token_hex(6).encode()).decode("utf-8")
        server.max_memory_usage = 4000
        server.max_cpu_usage = 2

        server.save()
        server.create(options_dict)

        return ServerStateMutation(server=server)


class Mutation(graphene.ObjectType):
    server_state = ServerStateMutation.Field()
    create_server = CreateServerMutation.Field()
    exec_command = ExecCommandMutation.Field()


class Query(graphene.ObjectType):
    all_servers = graphene.List(ServerType)
    server = graphene.Field(ServerType, server_id=graphene.String())
    all_templates = graphene.List(TemplateType)

    def resolve_all_servers(self, _info):
        """Returns a list of all servers that the requesting user can see"""

        return Server.objects.all()  # todo: only return servers user is authorized for

    def resolve_server(self, _info, server_id):
        """Returns the requested fields of the server selected by `server_id`

        Returns:
            Server: The server matching the query
        """

        return Server.objects.get(pk=server_id)  # todo: check if user is authorized to access the server

    def resolve_all_templates(self, _info):
        """Returns a list of all available app templates"""

        for file in os.scandir("app_templates.v2"):
            with open(file.path, 'r') as open_file:
                parsed = yaml.safe_load(open_file.read())
                name = file.name[:-4]
                title = parsed["name"]
                description = parsed["description"]
                yield {"name": name, "title": title, "description": description}


schema = graphene.Schema(query=Query, mutation=Mutation)
