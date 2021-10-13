import os
from typing import List

from django.test import TestCase
from graphene.test import Client
from api.schema import schema
from django.contrib.auth.models import User
import subprocess
import docker


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
        mutation createServer($name: String!, $description: String!, $port: Int!, $sftpPort: Int!, $allowedUsers: [ID]!, $template: String!) {
        
          createServer(
          name: $name,
          description: $description,
          port: $port,
          sftpPort: $sftpPort,
          allowedUsers: $allowedUsers,
          template: $template,
          options: {key: "VERSION", value: "1.17.1"}
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

        self.createServer("unittest_mt_server1", "Unittesting Minetest Server1", 34368, 34369, [self.user1.id], "minetest", ["TEST=33"])

        self.assertTrue(os.path.isdir(f"{os.environ['APP_DIR']}/unittest_mt_server1"))  # check if the app dir exists
        self.assertTrue(os.path.isfile(f"{os.environ['APP_DIR']}/unittest_mt_server1/docker-compose.yml"))  # check if compose file exists

        docker_client = docker.from_env()

        # verify both containers are running
        self.assertEqual("running", docker_client.containers.get("unittest_mt_server1_main_1").status)
        self.assertEqual("running", docker_client.containers.get("unittest_mt_server1_sftp_1").status)

        # remove test server
        subprocess.Popen(["docker-compose", "down"], cwd=f"{os.environ['APP_DIR']}/unittest_mt_server1").wait()
        subprocess.Popen(["rm", "-rf", "unittest_mt_server1"], cwd=os.environ['APP_DIR'])

    def test_create_too_high_port(self):
        """test if server creation fails on too high port number"""

        def create():
            self.createServer("unittest_mt_server1", "Unittesting Minetest Server1", 94368, 94369, [self.user1.id], "minetest", ["TEST=33"])
        self.assertRaisesMessage("port number must be between 1000 and 60000", create)

        # remove test server
        try:
            subprocess.Popen(["docker-compose", "down"], cwd=f"{os.environ['APP_DIR']}/unittest_mt_server1").wait()
            subprocess.Popen(["rm", "-rf", "unittest_mt_server1"], cwd=os.environ['APP_DIR'])
        except FileNotFoundError:
            pass  # expected behaviour

    def test_create_too_high_port_sftp(self):
        """test if server creation fails with too high sftp port"""

        def create():
            self.createServer("unittest_mt_server1", "Unittesting Minetest Server1", 34368, 94369, [self.user1.id], "minetest", ["TEST=33"])
        self.assertRaisesMessage("port number must be between 1000 and 60000", create)

        # remove test server
        try:
            subprocess.Popen(["docker-compose", "down"], cwd=f"{os.environ['APP_DIR']}/unittest_mt_server1").wait()
            subprocess.Popen(["rm", "-rf", "unittest_mt_server1"], cwd=os.environ['APP_DIR'])
        except FileNotFoundError:
            pass  # expected behaviour

    def test_create_too_low_port_sftp(self):
        """test if server creation fails with too low sftp port"""

        def create():
            self.createServer("unittest_mt_server1", "Unittesting Minetest Server1", 34368, 369, [self.user1.id], "minetest", ["TEST=33"])

        self.assertRaisesMessage("port number must be between 1000 and 60000", create)

        # remove test server
        try:
            subprocess.Popen(["docker-compose", "down"], cwd=f"{os.environ['APP_DIR']}/unittest_mt_server1").wait()
            subprocess.Popen(["rm", "-rf", "unittest_mt_server1"], cwd=os.environ['APP_DIR'])
        except FileNotFoundError:
            pass  # expected behaviour

    def test_create_too_low_port(self):
        """test if server creation fails with too low port"""

        def create():
            self.createServer("unittest_mt_server1", "Unittesting Minetest Server1", 368, 369, [self.user1.id], "minetest", ["TEST=33"])
        self.assertRaisesMessage("port number must be between 1000 and 60000", create)

        # remove test server
        try:
            subprocess.Popen(["docker-compose", "down"], cwd=f"{os.environ['APP_DIR']}/unittest_mt_server1").wait()
            subprocess.Popen(["rm", "-rf", "unittest_mt_server1"], cwd=os.environ['APP_DIR'])
        except FileNotFoundError:
            pass  # expected behaviour

    def test_create_invalid_name(self):
        """test if server creation fails with an invalid name"""

        def create():
            self.createServer("unittest_mt server1", "Unittesting Minetest Server1", 368, 369, [self.user1.id], "minetest", ["TEST=33"])
        self.assertRaisesMessage("server name may only contain lowercase letters, numbers and underscores", create)

        # remove test server
        try:
            subprocess.Popen(["docker-compose", "down"], cwd=f"{os.environ['APP_DIR']}/unittest_mt_server1").wait()
            subprocess.Popen(["rm", "-rf", "unittest_mt_server1"], cwd=os.environ['APP_DIR'])
        except FileNotFoundError:
            pass  # expected behaviour



