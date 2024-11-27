import unittest
from backend.src.app import create_app
from backend.src.models.user import User
from backend.src.models.links import Link, db
import json


class TestTaggingFeature(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app.testing = True
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            existing_user = User.query.filter_by(email="test_user@example.com").first()
            if existing_user:
                db.session.delete(existing_user)
                db.session.commit()
            # Create a test user
            test_user_data = {
                "email": "test_tags@gmail.com",
                "first_name": "Test",
                "last_name": "Tag",
                "password": "password",
            }
            self.client.post("/auth/register", json=test_user_data)
            response = self.client.post(
                "/auth/login",
                json={
                    "email": test_user_data["email"],
                    "password": test_user_data["password"],
                },
            )
            response_data = json.loads(response.data.decode('utf-8'))
            self.user = User.query.filter_by(email=test_user_data["email"]).first()
            self.token = response_data.get("token")
            self.headers = {
                # Include the token in the Authorization header
                'Authorization': f'Bearer {self.token}'
            }

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_tags_to_link(self):
        """Test adding tags to a link."""
        test_data = {
            "long_url": "https://example.com",
            "title": "Example Link",
            "tags": ["tag1", "tag2"]
        }
        response = self.client.post(
            "/links/create",
            json=test_data,
            query_string={"user_id": self.user.id},
            headers = self.headers
        )
        self.assertEqual(response.status_code, 201)

        with self.app.app_context():  # Wrap this query in an application context
            link = Link.query.filter_by(long_url="https://example.com").first()
            self.assertEqual(set(link.tags), {"tag1", "tag2"})

    def test_add_duplicate_tags_to_link(self):
        """Test that adding duplicate tags is handled correctly."""
        test_data = {
            "long_url": "https://example.com",
            "title": "Example Link with Duplicates",
            "tags": ["tag1", "tag1"]
        }
        response = self.client.post(
            "/links/create",
            json=test_data,
            query_string={"user_id": self.user.id},
            headers = self.headers
        )
        self.assertEqual(response.status_code, 201)

        with self.app.app_context():
            link = Link.query.filter_by(long_url="https://example.com").first()
            self.assertEqual(set(link.tags), {"tag1"})


    def test_query_links_by_tag(self):
        """Test querying links by a specific tag."""
        test_data = {
            "long_url": "https://tagquery.com",
            "title": "Tag Query Link",
            "tags": ["tag1"]
        }

        # Create the link using POST
        response = self.client.post(
            "/links/create",
            json=test_data,
            query_string={"user_id": self.user.id},
            headers = self.headers
        )
        self.assertEqual(response.status_code, 201)  # Check for successful creation

        # Debug: Check if the link was created with the right tags
        with self.app.app_context():
            created_link = Link.query.filter_by(long_url="https://tagquery.com").first()
            print("Created link tags:", created_link.tags)  # Print the tags to check

            link_id = created_link.id

            response = self.client.get('/links/' + str(link_id))
            self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()


