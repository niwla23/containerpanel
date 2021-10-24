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


class TemplateOptions(graphene.ObjectType):
    """Represents the template specific options. Ex.: server version, game mode

    Args:
        key (graphene.String): Key for the template option. Ex.: VERSION
        value (graphene.String): Value for the template option. Ex.: 1.17.1
    """
    key = graphene.String()
    value = graphene.String()
    description = graphene.String()


class TemplateType(graphene.ObjectType):
    """Represents an app templates in graphql"""

    name = graphene.String()
    title = graphene.String()
    description = graphene.String()
    options = graphene.List(TemplateOptions)


class UserType(DjangoObjectType):
    """Represents a django user in graphql"""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "id", "username")


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
    def mutate(cls, _root, info, server_id, action):
        server = Server.objects.get(pk=server_id)
        if server.is_user_allowed_to_manage(info.context.user):
            server.power_action(action)
            return ServerStateMutation(server=server)
        else:
            raise Exception("you are not allowed to manage this server")


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
    def mutate(cls, _root, info, server_id, command):
        server = Server.objects.get(pk=server_id)
        if server.is_user_allowed_to_manage(info.context.user):
            code, output = server.exec_command(command)
            return ExecCommandMutation(response=output, code=code)
        else:
            raise Exception("you are not allowed to manage this server")


class TemplateOptionsInput(graphene.InputObjectType):
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
        port = graphene.Int()
        sftp_port = graphene.Int()
        allowed_users = graphene.List(graphene.ID)
        options = graphene.List(TemplateOptionsInput)

    server = graphene.Field(ServerType)

    @classmethod
    def mutate(cls, _root, _info, name: str, description: str, template: str, port: int, sftp_port: int,
               allowed_users: list, options: list):
        if not isinstance(options, list):
            raise ValueError("options must be a list")

        if port > 60000 or port < 1000:
            raise ValueError("port number must be between 1000 and 60000")

        if sftp_port > 60000 or sftp_port < 1000:
            raise ValueError("port number must be between 1000 and 60000")

        if not re.match("^[a-z0-9_]+$", name):
            raise ValueError("server name may only contain lowercase letters, numbers and underscores")

        # todo: check if port is used #26

        print("fdfgsfgs", options)
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
        print(options_dict)
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
    template = graphene.Field(TemplateType, template_name=graphene.String())
    all_users = graphene.List(UserType)

    def resolve_all_servers(self, info):
        """Returns a list of all servers that the requesting user can see"""
        user = info.context.user

        return Server.objects.filter(allowed_users__in=[user])  # todo: only return servers user is authorized for

    def resolve_server(self, info, server_id):
        """Returns the requested fields of the server selected by `server_id`

        Returns:
            Server: The server matching the query
        """
        user = info.context.user

        result: Server = Server.objects.get(pk=server_id)
        if result.is_user_allowed_to_manage(user):
            return result
        else:
            raise Exception("you are not allowed to manage this server")

    def resolve_all_templates(self, _info):
        """Returns a list of all available app templates"""

        for file in os.scandir("app_templates.v2"):
            with open(file.path, 'r') as open_file:
                parsed = yaml.safe_load(open_file.read())
                name = file.name[:-4]
                title = parsed["name"]
                description = parsed["description"]
                yield {"name": name, "title": title, "description": description}

    def resolve_template(self, _info, template_name):
        """Returns details for the specified template name"""

        with open(f"app_templates.v2/{template_name}.yml", 'r') as open_file:
            parsed = yaml.safe_load(open_file.read())
            name = template_name
            title = parsed["name"]
            description = parsed["description"]
            options = parsed["options"]
            options = [] if not options else options
            options_formatted = []
            for option in options:
                option_formatted = TemplateOptions()
                option_formatted.key = option["key"]
                option_formatted.value = option["value"]
                option_formatted.description = option["description"]
                options_formatted.append(option_formatted)
            return {"name": name, "title": title, "description": description, "options": options_formatted}

    def resolve_all_users(self, _info):
        return User.objects.all()


schema = graphene.Schema(query=Query, mutation=Mutation)
