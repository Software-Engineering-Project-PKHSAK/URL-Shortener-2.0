import unittest
from backend.src.app import create_app
from backend.src.models.user import User
from backend.src.models.links import Link, db

class TestTaggingFeature(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()

        with self.app.app_context():
            test_user_data = {
                "email": "test_tags@gmail.com",
                "first_name": "Test",
                "last_name": "Tag",
                "password": "password",
            }
            self.client.post("/auth/register", json=test_user_data)
            self.client.post(
                "/auth/login",
                json={
                    "email": test_user_data["email"],
                    "password": test_user_data["password"],
                },
            )
            self.user = User.query.filter_by(email=test_user_data["email"]).first()

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
        )
        self.assertEqual(response.status_code, 201)

        with self.app.app_context():
            link = Link.query.filter_by(long_url="https://example.com").first()
            self.assertEqual(set(link.tags), {"tag1"})

    def test_update_link_tags(self):
        """Test updating the tags of an existing link."""
        initial_data = {
            "long_url": "https://updatable.com",
            "title": "Updatable Link",
            "tags": ["tag1"]
        }
        self.client.post(
            "/links/create",
            json=initial_data,
            query_string={"user_id": self.user.id},
        )
        update_data = {
            "tags": ["tag2", "tag3"]
        }
        response = self.client.put(
            "/links/update_tags",
            json=update_data,
            query_string={"link_id": Link.query.filter_by(long_url="https://updatable.com").first().id},
        )
        self.assertEqual(response.status_code, 200)

        with self.app.app_context():  # Wrap this query in an application context
            updated_link = Link.query.filter_by(long_url="https://updatable.com").first()
            self.assertEqual(set(updated_link.tags), {"tag2", "tag3"})

    def test_remove_tag_from_link(self):
        """Test removing a tag from an existing link."""
        test_data = {
            "long_url": "https://removable.com",
            "title": "Removable Tag Link",
            "tags": ["tag1", "tag2"]
        }
        self.client.post(
            "/links/create",
            json=test_data,
            query_string={"user_id": self.user.id},
        )

        remove_data = {
            "tags": ["tag1"]  # Fix typo from "tags1" to "tag1"
        }

        with self.app.app_context():
            link_id = Link.query.filter_by(long_url="https://removable.com").first().id

        response = self.client.put(
            "/links/update_tags",
            json=remove_data,
            query_string={"link_id": link_id},
        )
        self.assertEqual(response.status_code, 405)

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
        )
        self.assertEqual(response.status_code, 201)  # Check for successful creation

        # Debug: Check if the link was created with the right tags
        with self.app.app_context():
            created_link = Link.query.filter_by(long_url="https://tagquery.com").first()
            print("Created link tags:", created_link.tags)  # Print the tags to check

            link_id = created_link.id
            response = self.app.get('/links/' + str(link_id))
            self.assertEqual(response.status_code, 201)


    def tearDown(self):
        """Clean up test database."""
        with self.app.app_context():  # Ensure application context is active
            db.session.query(Link).filter_by(user_id=self.user.id).delete()
            db.session.query(User).filter_by(email="test_tags@gmail.com").delete()
            db.session.commit()

if __name__ == "__main__":
    unittest.main()


