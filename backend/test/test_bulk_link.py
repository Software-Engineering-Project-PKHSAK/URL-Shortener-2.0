import unittest
from backend.src.app import create_app
from backend.src.models.user import User
from backend.src.models.links import Link, db
from backend.src.routes.links import create_unique_stub
import json

class TestBulkLinkCreation(unittest.TestCase):
    def setUp(self):
        """Set up test client and create test user for authentication."""
        self.app = create_app("testing")
        self.client = create_app("testing").test_client()
        
        with self.app.app_context():
            db.create_all()
            existing_user = User.query.filter_by(email="test_bulk@gmail.com").first()
            if existing_user:
                db.session.delete(existing_user)
                db.session.commit()
            # Register and log in test user
            test_user_data = {
                "email": "test_bulk@gmail.com",
                "first_name": "Test",
                "last_name": "Bulk",
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

    def test_create_unique_stub(self):
        """Test unique stub generation without database duplicates."""
        with self.app.app_context():
            for _ in range(10):
                stub = create_unique_stub()
                already_exists = db.session.query(db.exists().where(Link.stub == stub)).scalar()
                self.assertFalse(already_exists)

    def test_bulk_create_links_success(self):
        """Test successful bulk link creation."""
        test_data = {
            "links": [
                {"long_url": "https://example1.com", "title": "Example 1"},
                {"long_url": "https://example2.com", "title": "Example 2"},
            ]
        }
        response = self.client.post(
            "/links/create_bulk",
            json=test_data,
            query_string={"user_id": self.user.id},
            headers = self.headers
        )
        self.assertEqual(response.status_code, 201)
        response_data = response.get_json()
        self.assertEqual(len(response_data["links"]), 2)
        self.assertEqual(response_data["message"], "Bulk link creation successful")

    def test_bulk_create_missing_title(self):
        """Ensure creation fails if a required title is missing in the payload."""
        test_data = {"links": [{"long_url": "https://example.com"}]}
        response = self.client.post(
            "/links/create_bulk",
            json=test_data,
            query_string={"user_id": self.user.id},
            headers = self.headers
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Long URL and title are required", response.get_json()["message"])

    def test_bulk_create_invalid_json_format(self):
        """Test for invalid JSON structure in request payload."""
        test_data = {"incorrect_key": []}
        response = self.client.post(
            "/links/create_bulk",
            json=test_data,
            query_string={"user_id": self.user.id},
            headers = self.headers
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("No links data provided", response.get_json()["message"])

    def test_bulk_create_with_existing_stub(self):
        """Ensure stubs are unique, even if identical stubs are requested."""
        with self.app.app_context():
            test_data = {
                "links": [{"long_url": "https://unique-stub.com", "title": "Unique Stub"}]
            }
            self.client.post(
                "/links/create_bulk",
                json=test_data,
                query_string={"user_id": self.user.id},
                headers = self.headers
            )
            link = Link.query.filter_by(long_url="https://unique-stub.com").order_by(Link.created_on.asc()).first()
            # Create another link to check unique stub generation
            response = self.client.post(
                "/links/create_bulk",
                json=test_data,
                query_string={"user_id": self.user.id},
                headers = self.headers
            )
            self.assertEqual(response.status_code, 201)
            new_link = Link.query.filter_by(long_url="https://unique-stub.com").order_by(Link.created_on.desc()).first()
            self.assertNotEqual(link.stub, new_link.stub)

    def test_bulk_create_with_expiration(self):
        """Test bulk creation with expiration date set for each link."""
        test_data = {
            "links": [
                {
                    "long_url": "https://expirable.com",
                    "title": "Expirable Link",
                    "expire_on": "2024-12-31T23:59:59",
                }
            ]
        }
        response = self.client.post(
            "/links/create_bulk",
            json=test_data,
            query_string={"user_id": self.user.id},
            headers = self.headers
        )
        with self.app.app_context():
            self.assertEqual(response.status_code, 201)
            link = Link.query.filter_by(long_url="https://expirable.com").first()
            self.assertIsNotNone(link.expire_on)

    def test_bulk_create_with_disabled_links(self):
        """Test creating links in bulk with some links disabled initially."""
        test_data = {
            "links": [
                {
                    "long_url": "https://disabled1.com",
                    "title": "Disabled Link 1",
                    "disabled": True,
                },
                {
                    "long_url": "https://enabled1.com",
                    "title": "Enabled Link 1",
                    "disabled": False,
                },
            ]
        }
        response = self.client.post(
            "/links/create_bulk",
            json=test_data,
            query_string={"user_id": self.user.id},
            headers = self.headers
        )
        self.assertEqual(response.status_code, 201)
        with self.app.app_context():
            disabled_link = Link.query.filter_by(long_url="https://disabled1.com").first()
            enabled_link = Link.query.filter_by(long_url="https://enabled1.com").first()
            self.assertTrue(disabled_link.disabled)
            self.assertFalse(enabled_link.disabled)

    def test_bulk_create_links_utm_parameters(self):
        """Test if UTM parameters are correctly stored during bulk link creation."""
        test_data = {
            "links": [
                {
                    "long_url": "https://utm.com",
                    "title": "UTM Test",
                    "utm_source": "source",
                    "utm_medium": "medium",
                    "utm_campaign": "campaign",
                }
            ]
        }
        response = self.client.post(
            "/links/create_bulk",
            json=test_data,
            query_string={"user_id": self.user.id},
            headers = self.headers
        )
        self.assertEqual(response.status_code, 201)
        with self.app.app_context():
            link = Link.query.filter_by(long_url="https://utm.com").first()
            self.assertEqual(link.utm_source, "source")
            self.assertEqual(link.utm_medium, "medium")
            self.assertEqual(link.utm_campaign, "campaign")

    def test_bulk_create_with_password_protection(self):
        """Test bulk creation with password-protected links."""
        test_data = {
            "links": [
                {
                    "long_url": "https://protected.com",
                    "title": "Password Protected",
                    "password_hash": "hashed_password",
                }
            ]
        }
        response = self.client.post(
            "/links/create_bulk",
            json=test_data,
            query_string={"user_id": self.user.id},
            headers = self.headers
        )
        with self.app.app_context():
            self.assertEqual(response.status_code, 201)
            link = Link.query.filter_by(long_url="https://protected.com").first()
            self.assertEqual(link.password_hash, "hashed_password")

    def test_bulk_create_duplicate_long_url(self):
        """Test if creating duplicate long URLs in bulk is handled correctly."""
        test_data = {
            "links": [
                {"long_url": "https://duplicate.com", "title": "Duplicate Link 1"},
                {"long_url": "https://duplicate.com", "title": "Duplicate Link 2"},
            ]
        }
        response = self.client.post(
            "/links/create_bulk",
            json=test_data,
            query_string={"user_id": self.user.id},
            headers = self.headers
        )
        with self.app.app_context():
            self.assertEqual(response.status_code, 201)
            links = Link.query.filter_by(long_url="https://duplicate.com").all()
            self.assertEqual(len(links), 2)
            self.assertNotEqual(links[0].stub, links[1].stub)

if __name__ == "__main__":
    unittest.main()