import unittest
from unittest.mock import patch
from flask import json
import sys
import os
import uuid  # Import uuid to create test UUIDs

# Add the src directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from app import app, db  # Assuming your app is named "app.py" and "app" is the Flask instance.
from src.models.user import User  # Importing the User model
from src.models.links import Link  # Importing the Link model for the link tests

class TestLinkAPI(unittest.TestCase):
    def setUp(self):
        # Setup runs before each test
        app.config.from_object('src.config.TestingConfig')
        self.app = app.test_client()
        self.app.testing = True

        # Add a user for testing
        with app.app_context():
            db.create_all()
            user = User(
                id=uuid.uuid4(),
                email="testuser@example.com",
                first_name="Test",
                last_name="User",
                password_hash="hashed_password"  # Assuming this is already hashed for testing
            )
            db.session.add(user)
            db.session.commit()
            self.user_id = user.id

    def tearDown(self):
        # Teardown runs after each test
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_bulk_links_success(self):
        # Arrange
        bulk_data = {
            "links": [
                {"long_url": "https://example.com/1", "title": "Example 1"},
                {"long_url": "https://example.com/2", "title": "Example 2"},
                {"long_url": "https://example.com/3"},
                {"long_url": "https://example.com/4", "utm_source": "source4"},
                {"long_url": "https://example.com/5", "title": "Example 5", "utm_medium": "medium5"},
                {"long_url": "https://example.com/6", "utm_campaign": "campaign6"},
                {"long_url": "https://example.com/7", "title": "Example 7", "utm_term": "term7"},
                {"long_url": "https://example.com/8", "utm_content": "content8"},
                {"long_url": "https://example.com/9", "title": "Example 9", "disabled": True},
                {"long_url": "https://example.com/10", "expire_on": "2024-12-31"}
            ]
        }
        headers = {
            'Content-Type': 'application/json'
        }

        # Act
        response = self.app.post(f'/links/create_bulk?user_id={self.user_id}',
                                 data=json.dumps(bulk_data),
                                 headers=headers)
        response_data = json.loads(response.data)

        # Assert
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_data['status'], 201)
        self.assertEqual(len(response_data['links']), 10)
        self.assertEqual(response_data['message'], 'Bulk link creation successful')

    def test_create_bulk_links_missing_data(self):
        # Arrange
        bulk_data = {
            "links": [
                {"title": "Missing URL"},
                {"utm_source": "source1"},
                {"utm_medium": "medium2"},
                {"utm_campaign": "campaign3"},
                {"utm_term": "term4"},
                {"utm_content": "content5"},
                {"disabled": True},
                {"expire_on": "2024-12-31"},
                {"title": "Missing URL 2"},
                {"utm_source": "source6", "utm_medium": "medium6"}
            ]
        }
        headers = {
            'Content-Type': 'application/json'
        }

        # Act
        response = self.app.post(f'/links/create_bulk?user_id={self.user_id}',
                                 data=json.dumps(bulk_data),
                                 headers=headers)
        response_data = json.loads(response.data)

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['status'], 400)
        self.assertEqual(response_data['message'], "Bulk link creation failed: 'long_url'")

    def test_redirect_stub_success(self):
        # Arrange
        with app.app_context():
            link = Link(
                user_id=self.user_id,
                stub='abc123',
                long_url='https://example.com/redirect',
                title='Example Redirect'
            )
            db.session.add(link)
            db.session.commit()

        # Act
        response = self.app.get('/abc123')

        # Assert
        self.assertEqual(response.status_code, 302)  # 302 is the HTTP status code for redirects
        self.assertEqual(response.location, 'https://example.com/redirect')

    def test_redirect_stub_not_found(self):
        # Act
        response = self.app.get('/notfound123')
        response_data = json.loads(response.data)

        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_data['status'], 404)
        self.assertEqual(response_data['message'], 'Link not found.')

if __name__ == '__main__':
    unittest.main()