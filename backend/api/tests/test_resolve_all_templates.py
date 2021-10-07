from django.test import TestCase
from graphene.test import Client

from api.schema import schema


class ResolveAllTemplatesTestCase(TestCase):
    """Contains tests to check the list of templates is correct"""

    def test_resolve_all_templates(self):
        """tests if the list of templates returned is correct"""

        client = Client(schema)
        query = """
query allTemplates {
  allTemplates {
    name
    title
    description
  }
}
        """
        response = client.execute(
            query
        )
        self.assertGreater(len(response["data"]["allTemplates"]), 1)
        self.assertGreater(len(response["data"]["allTemplates"][0]["name"]), 0)
        self.assertGreater(len(response["data"]["allTemplates"][0]["title"]), 0)
        self.assertGreater(len(response["data"]["allTemplates"][0]["description"]), 0)
