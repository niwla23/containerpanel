import asyncio
import base64
import secrets

import graphene
import os

import yaml
from asgiref.sync import sync_to_async

from api.models import Server
from graphene_django import DjangoObjectType
from django.contrib.auth.models import User


class ServerStateType(graphene.ObjectType):
    running = graphene.Boolean()
    cpu_usage = graphene.Float()
    memory_usage = graphene.Float()


class ServerType(DjangoObjectType):
    state = graphene.Field(ServerStateType)
    logs = graphene.List(graphene.String)

    def resolve_state(self, info):
        server = Server.objects.get(pk=self.server_id)
        cpu_usage, memory_usage = server.stats
        return {
            "running": server.running,
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage
        }

    def resolve_logs(self, info):
        server = Server.objects.get(pk=self.server_id)
        return server.get_logs(50)

    class Meta:
        model = Server
        fields = ("server_id", "description", "name", "command_prefix", "allowed_users", "port", "sftp_port")


class TemplateType(graphene.ObjectType):
    name = graphene.String()
    title = graphene.String()
    description = graphene.String()


@sync_to_async
def get_server_async(server_id: str):
    return Server.objects.get(pk=server_id)


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "id")


class ServerStateMutation(graphene.Mutation):
    class Arguments:
        server_id = graphene.ID()
        action = graphene.String()

    # The class attributes define the response of the mutation
    server = graphene.Field(ServerType)

    @classmethod
    def mutate(cls, root, info, server_id, action):
        server = Server.objects.get(pk=server_id)
        server.power_action(action)
        return ServerStateMutation(server=server)


class ExecCommandMutation(graphene.Mutation):
    class Arguments:
        server_id = graphene.ID()
        command = graphene.String()

    # The class attributes define the response of the mutation
    response = graphene.String()
    code = graphene.Int()

    @classmethod
    def mutate(cls, root, info, server_id, command):
        server = Server.objects.get(pk=server_id)
        code, output = server.exec_command(command)
        return ExecCommandMutation(response=output, code=code)


class CreateServerMutation(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        description = graphene.String()
        template = graphene.String()
        options = graphene.List(graphene.String)
        port = graphene.Int()
        sftp_port = graphene.Int()
        allowed_users = graphene.List(graphene.ID)

    server = graphene.Field(ServerType)

    @classmethod
    def mutate(cls, root, info, name: str, description: str, template: str, options: dict, port: int, sftp_port: int,
               allowed_users: list):
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
        server.create()

        return ServerStateMutation(server=server)


class Mutation(graphene.ObjectType):
    server_state = ServerStateMutation.Field()
    create_server = CreateServerMutation.Field()
    exec_command = ExecCommandMutation.Field()


class Query(graphene.ObjectType):
    all_servers = graphene.List(ServerType)
    server = graphene.Field(ServerType, server_id=graphene.String())
    all_templates = graphene.List(TemplateType)

    def resolve_all_servers(self, info):
        return Server.objects.all()

    def resolve_server(self, info, server_id):
        return Server.objects.get(pk=server_id)

    def resolve_all_templates(self, info):
        for file in os.scandir("app_templates.v2"):
            with open(file, 'r') as open_file:
                parsed = yaml.safe_load(open_file.read())
                name = file.name[:-4]
                title = parsed["name"]
                description = parsed["description"]
                yield {"name": name, "title": title, "description": description}


schema = graphene.Schema(query=Query, mutation=Mutation)
