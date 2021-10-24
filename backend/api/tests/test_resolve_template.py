from django.test import TestCase
from graphene.test import Client

from api.schema import schema


class ResolveAllTemplatesTestCase(TestCase):
    """Contains tests to check if single template requests are handled correctly"""

    def test_resolve_airplane_template(self):
        """test if the response for minecraft airplane is correct"""

        client = Client(schema)
        query = """
query template {
  template(templateName: "mc_airplane") {
    name
    description
    options {
      key
      value
    }
  }
}
        """
        response = client.execute(
            query
        )
        self.assertEqual(response["data"]["template"]["name"], "mc_airplane")
        self.assertGreater(len(response["data"]["template"]["description"]), 4)
        self.assertGreater(len(response["data"]["template"]["options"][0]["key"]), 0)
        self.assertGreater(len(response["data"]["template"]["options"][0]["value"]), 0)
