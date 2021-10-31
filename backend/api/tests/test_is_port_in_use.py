import subprocess
import docker
from api.helpers import is_port_in_use
from django.test import TestCase
import time


class ResolveAllTemplatesTestCase(TestCase):
    """Contains tests to check the is_port_in_use function."""

    def test_non_docker_port_used_true(self):
        """test if a port that is used by a host process is detected as being used."""

        server = subprocess.Popen(["python3", "-m", "http.server", "23764"])  # most hacky solution i could find
        time.sleep(2)
        result = is_port_in_use(23764)
        self.assertTrue(result)
        server.kill()

    def test_docker_port_used_true(self):
        """test if a port that is used by a docker container is detected as being used."""

        client = docker.from_env()
        container_id = subprocess.check_output(["docker", "run", "-d", "-p", "23765:23765", "ubuntu", "sleep", "222"])
        time.sleep(2)
        container = client.containers.get(container_id.decode()[:-2])

        result = is_port_in_use(23765)
        self.assertTrue(result)
        container.remove(force=True)

    def test_port_not_used(self):
        """test if a port that is used by a host process is detected as being used."""
        result = is_port_in_use(2376)
        self.assertFalse(result)

