import os
import subprocess
from typing import List

import docker
from django.contrib.auth.models import User
from django.test import TestCase
from graphene.test import Client

from api.schema import schema


class CreateServerMutationTestCase(TestCase):
    """Contains tests for creating servers"""

    def setUp(self) -> None:
        """creates a user that we assign the servers to."""

        self.user1 = User.objects.create_user("user1", "user1@example.com", "5R64o!f84")

    def createServer(self, name: str, description: str, port: int, sftp_port: int, allowed_users: List[int], template: str, options: List[str]):
        """helper function to create a server

        Creates a new server using the graphql api.

        Args:
            name (str): Name of the server
            description (str): human-readable name of the server
            port (int): port of the main container connected to this server
            sftp_port (int): port of the sftp container connected to this server
            allowed_users (list): list of user ids allowed to manage the server
            template (str): template for the server
            options (list): List of strings for template specific options
        """

        client = Client(schema)

        query = """
              mutation createServer(
              $name: String!,
              $description: String!,
              $port: Int!,
              $sftpPort: Int!,
              $allowedUsers: [ID]!,
              $template: String!,
              $options: [TemplateOptionsInput]
              )
              {
              createServer(
                name: $name,
                description: $description,
                port: $port,
                sftpPort: $sftpPort,
                allowedUsers: $allowedUsers,
                template: $template,
                options: $options
                
                ) {
                server {
                  serverId
                }
              }
            }
        """
        client.execute(
            query,
            variable_values={
                "name": name,
                "description": description,
                "port": port,
                "sftpPort": sftp_port,
                "allowedUsers": allowed_users,
                "template": template,
                "options": options
            }
        )

    def test_create_correct_mt_server(self):
        """test if normal server creation works"""

        name = "unittest_mt_server1"

        self.createServer(name, "Unittesting Minetest Server1", 34368, 34369, [self.user1.id], "minetest", [])

        self.assertTrue(os.path.isdir(f"{os.environ['APP_DIR']}/{name}"))  # check if the app dir exists
        self.assertTrue(os.path.isfile(f"{os.environ['APP_DIR']}/{name}/docker-compose.yml"))  # check if compose file exists

        docker_client = docker.from_env()

        # verify both containers are running
        self.assertEqual("running", docker_client.containers.get(f"{name}_main_1").status)
        self.assertEqual("running", docker_client.containers.get(f"{name}_sftp_1").status)

        # verify timezone
        with open(f"{os.environ['APP_DIR']}/{name}/docker-compose.yml", "r") as compose_file:
            self.assertTrue("TZ:" in compose_file.read())

        # remove test server
        subprocess.Popen(["docker-compose", "down"], cwd=f"{os.environ['APP_DIR']}/{name}").wait()
        subprocess.Popen(["rm", "-rf", name], cwd=os.environ['APP_DIR'])

    def test_create_too_high_port(self):
        """test if server creation fails on too high port number"""
        name = "unittest_mt_server2"

        def create():
            self.createServer(name, "Unittesting Minetest Server1", 94368, 94369, [self.user1.id], "minetest", [])

        self.assertRaisesMessage("port number must be between 1000 and 60000", create)

        # remove test server
        try:
            subprocess.Popen(["docker-compose", "down"], cwd=f"{os.environ['APP_DIR']}/{name}").wait()
            subprocess.Popen(["rm", "-rf", name], cwd=os.environ['APP_DIR'])
        except FileNotFoundError:
            pass  # expected behaviour

    def test_create_too_high_port_sftp(self):
        """test if server creation fails with too high sftp port"""

        name = "unittest_mt_server3"

        def create():
            self.createServer(name, "Unittesting Minetest Server1", 34368, 94369, [self.user1.id], "minetest", [])

        self.assertRaisesMessage("port number must be between 1000 and 60000", create)

        # remove test server
        try:
            subprocess.Popen(["docker-compose", "down"], cwd=f"{os.environ['APP_DIR']}/{name}").wait()
            subprocess.Popen(["rm", "-rf", name], cwd=os.environ['APP_DIR'])
        except FileNotFoundError:
            pass  # expected behaviour

    def test_create_too_low_port_sftp(self):
        """test if server creation fails with too low sftp port"""

        name = "unittest_mt_server4"

        def create():
            self.createServer(name, "Unittesting Minetest Server1", 34368, 369, [self.user1.id], "minetest", [])

        self.assertRaisesMessage("port number must be between 1000 and 60000", create)

        # remove test server
        try:
            subprocess.Popen(["docker-compose", "down"], cwd=f"{os.environ['APP_DIR']}/{name}").wait()
            subprocess.Popen(["rm", "-rf", name], cwd=os.environ['APP_DIR'])
        except FileNotFoundError:
            pass  # expected behaviour

    def test_create_too_low_port(self):
        """test if server creation fails with too low port"""

        name = "unittest_mt_server5"

        def create():
            self.createServer(name, "Unittesting Minetest Server1", 368, 369, [self.user1.id], "minetest", [])

        self.assertRaisesMessage("port number must be between 1000 and 60000", create)

        # remove test server
        try:
            subprocess.Popen(["docker-compose", "down"], cwd=f"{os.environ['APP_DIR']}/{name}").wait()
            subprocess.Popen(["rm", "-rf", name], cwd=os.environ['APP_DIR'])
        except FileNotFoundError:
            pass  # expected behaviour

    def test_create_invalid_name(self):
        """test if server creation fails with an invalid name"""
        name = "unittest mt_server6"

        def create():
            self.createServer(name, "Unittesting Minetest Server1", 368, 369, [self.user1.id], "minetest", [])

        self.assertRaisesMessage("server name may only contain lowercase letters, numbers and underscores", create)

        # remove test server
        try:
            subprocess.Popen(["docker-compose", "down"], cwd=f"{os.environ['APP_DIR']}/{name}").wait()
            subprocess.Popen(["rm", "-rf", name], cwd=os.environ['APP_DIR'])
        except FileNotFoundError:
            pass  # expected behaviour

    def test_create_server_folder_exists(self):
        """test if server creation fails when directory exists"""
        name = "unittest_app_dir_exists"
        path = f"{os.environ['APP_DIR']}/{name}"

        try:
            os.rmdir(path)
        except FileNotFoundError:
            pass

        os.mkdir(path)

        def create():
            self.createServer(name, "Unittesting Minetest Server1", 34368, 34369, [self.user1.id], "minetest", [])

        self.assertRaisesMessage("path is not empty", create)

        os.rmdir(path)
        # remove test server
        try:
            subprocess.Popen(["docker-compose", "down"], cwd=f"{os.environ['APP_DIR']}/{name}").wait()
            subprocess.Popen(["rm", "-rf", name], cwd=os.environ['APP_DIR'])
        except FileNotFoundError:
            pass  # expected behaviour

    def test_create_server_name_exists(self):
        """test if server creation fails when server name is used"""
        name = "unittest_name_duplicate"

        self.createServer(name, "Unittesting Minetest Server1", 34368, 34369, [self.user1.id], "minetest", [])

        def create():
            self.createServer(name, "Unittesting Minetest Server1", 34368, 34369, [self.user1.id], "minetest", [])

        self.assertRaisesMessage("path is not empty", create)

        # remove test server
        try:
            subprocess.Popen(["docker-compose", "down"], cwd=f"{os.environ['APP_DIR']}/{name}").wait()
            subprocess.Popen(["rm", "-rf", name], cwd=os.environ['APP_DIR'])
        except FileNotFoundError:
            pass
