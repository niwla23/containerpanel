from api.models import Server
from django.contrib.auth.models import User

from django.test import TestCase


class ResolveAllTemplatesTestCase(TestCase):
    """Contains tests to check the list of templates is correct"""

    def setUp(self) -> None:
        """creates a server and a few users for testing"""
        self.user1 = User.objects.create_user("user1", "user1@example.com", "5R64o!f84")
        self.user2 = User.objects.create_user("user2", "user2@example.com", "bD4hD-54f")
        self.user3 = User.objects.create_user("user3", "user3@example.com", "ijgf94j8jh")
        self.superuser1 = User.objects.create_superuser("superuser1", "superuser1@example.com", "jf8034hj9")
        self.staff1 = User.objects.create_user("staff1", "staff1@example.com", "fef3f3f3", is_staff=True)

        self.server1 = Server()
        self.server1.name = "unit_testing_test_server"
        self.server1.description = "Unit testing test server"
        self.server1.template = "minetest"
        self.server1.port = 39999
        self.server1.sftp_port = 39998
        self.server1.max_cpu_usage = 400
        self.server1.max_memory_usage = 100000

        self.server1.save()
        self.server1.allowed_users.set([])  # Initially no users are allowed to access this server
        self.server1.save()

    def test_superuser_can_access_server_with_no_managers(self):
        """test if a superuser account can access a server with no configured managers"""
        self.server1.allowed_users.set([])
        self.assertTrue(self.server1.is_user_allowed_to_manage(self.superuser1))

    def test_superuser_can_access_server_with_normal_managers(self):
        """test if a superuser account can access a server with normal user managers"""
        self.server1.allowed_users.set([self.user1, self.user3])
        self.assertTrue(self.server1.is_user_allowed_to_manage(self.superuser1))

    def test_staff_can_access_server_with_no_managers(self):
        """test if a staff account can access a server with no configured managers"""
        self.server1.allowed_users.set([])
        self.assertTrue(self.server1.is_user_allowed_to_manage(self.staff1))

    def test_staff_can_access_server_with_normal_managers(self):
        """test if a staff account can access a server with normal user managers"""
        self.server1.allowed_users.set([self.user1, self.user3])
        self.assertTrue(self.server1.is_user_allowed_to_manage(self.staff1))

    def test_allowed_user_can_manage_server(self):
        """test if an allowed user can manage the server"""
        self.server1.allowed_users.set([self.user1, self.user3])
        self.assertTrue(self.server1.is_user_allowed_to_manage(self.user1))
        self.assertTrue(self.server1.is_user_allowed_to_manage(self.user3))

    def test_not_allowed_user_can_not_manage_server(self):
        """test if a not allowed user can not manage the server"""
        self.server1.allowed_users.set([self.user1, self.user3])
        self.assertFalse(self.server1.is_user_allowed_to_manage(self.user2))

    def test_no_normal_user_can_manage_if_allowed_users_empty(self):
        """test if no normal user can manage the server if no users are configured"""
        self.server1.allowed_users.set([])
        self.assertFalse(self.server1.is_user_allowed_to_manage(self.user1))
        self.assertFalse(self.server1.is_user_allowed_to_manage(self.user2))
        self.assertFalse(self.server1.is_user_allowed_to_manage(self.user3))
