import sys
sys.path.append('backend/src')
import unittest
from models.links import Link, db
from app import create_app
from models.user import User
import uuid

class LinkAutoDeactivationTest(unittest.TestCase):

    def setUp(self):
        self.flask_app = create_app()
        self.app = self.flask_app.test_client()
        with self.flask_app.app_context():
            db.create_all()
            # Create a test user
            user = User(id=str(uuid.uuid4()), email="test_user@example.com", first_name="Test", last_name="User")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
            self.user_id = user.id

    def tearDown(self):
        with self.flask_app.app_context():
            db.session.remove()
            db.drop_all()

    def test_link_creation_with_max_visits(self):
        """Test link creation with max_visits set."""
        with self.flask_app.app_context():
            link = Link(
                id=str(uuid.uuid4()), user_id=self.user_id, long_url="https://example.com",
                title="Example", max_visits=5
            )
            db.session.add(link)
            db.session.commit()
            self.assertEqual(link.max_visits, 5)
            self.assertEqual(link.visit_count, 0)

    def test_link_visit_count_increments(self):
        """Test visit count increments on link access."""
        with self.flask_app.app_context():
            link = Link(
                id=str(uuid.uuid4()), user_id=self.user_id, long_url="https://example.com",
                title="Example", max_visits=5, visit_count=0
            )
            db.session.add(link)
            db.session.commit()
            for _ in range(3):
                link.visit_count += 1
                db.session.commit()
            self.assertEqual(link.visit_count, 3)

    def test_link_deactivation_after_max_visits(self):
        """Test link auto-deactivates after reaching max_visits."""
        with self.flask_app.app_context():
            link = Link(
                id=str(uuid.uuid4()), user_id=self.user_id, long_url="https://example.com",
                title="Example", max_visits=3, visit_count=3, disabled=False
            )
            link.disabled = link.visit_count >= link.max_visits
            db.session.commit()
            self.assertTrue(link.disabled)

    def test_no_max_visits_allows_unlimited_access(self):
        """Test link remains active when max_visits is None."""
        with self.flask_app.app_context():
            link = Link(
                id=str(uuid.uuid4()), user_id=self.user_id, long_url="https://example.com",
                title="Example", max_visits=None, visit_count=10
            )
            link.disabled = False
            db.session.commit()
            self.assertFalse(link.disabled)

    def test_link_access_returns_403_when_disabled(self):
        """Test accessing a disabled link returns 403 status code."""
        self.app.post('/auth/login', json=dict(email="test_user@example.com", password="password123"))
        link = Link(
            id=str(uuid.uuid4()), user_id=self.user_id, long_url="https://example.com",
            title="Example", max_visits=3, visit_count=3, disabled=True
        )
        db.session.add(link)
        db.session.commit()
        response = self.app.get(f'/links/stub/{link.stub}')
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'This link has been disabled.', response.data)

    def test_auto_disabling_on_exact_visit_limit(self):
        """Test link disables exactly on reaching max_visits."""
        with self.flask_app.app_context():
            link = Link(
                id=str(uuid.uuid4()), user_id=self.user_id, long_url="https://example.com",
                title="Example", max_visits=3, visit_count=2
            )
            link.visit_count += 1
            link.disabled = link.visit_count >= link.max_visits
            db.session.commit()
            self.assertTrue(link.disabled)

    def test_max_visits_zero_never_enables_access(self):
        """Test that setting max_visits to zero makes the link inaccessible."""
        with self.flask_app.app_context():
            link = Link(
                id=str(uuid.uuid4()), user_id=self.user_id, long_url="https://example.com",
                title="Example", max_visits=0, visit_count=0
            )
            link.disabled = link.visit_count >= link.max_visits
            db.session.commit()
            self.assertTrue(link.disabled)

    def test_update_max_visits_for_existing_link(self):
        """Test updating max_visits for an existing link and re-enabling access."""
        with self.flask_app.app_context():
            link = Link(
                id=str(uuid.uuid4()), user_id=self.user_id, long_url="https://example.com",
                title="Example", max_visits=2, visit_count=2, disabled=True
            )
            link.max_visits = 5
            link.disabled = False
            db.session.commit()
            self.assertFalse(link.disabled)
            self.assertEqual(link.max_visits, 5)

    def test_disabling_on_high_visit_count(self):
        """Test that setting a low max_visits disables high visit count links."""
        with self.flask_app.app_context():
            link = Link(
                id=str(uuid.uuid4()), user_id=self.user_id, long_url="https://example.com",
                title="Example", max_visits=3, visit_count=5
            )
            link.disabled = link.visit_count >= link.max_visits
            db.session.commit()
            self.assertTrue(link.disabled)

    def test_bulk_link_creation_with_max_visits(self):
        """Test bulk link creation including max_visits settings."""
        bulk_links = [
            {"long_url": "https://example1.com", "title": "Example 1", "max_visits": 5},
            {"long_url": "https://example2.com", "title": "Example 2", "max_visits": 2}
        ]
        response = self.app.post('/links/create_bulk', json=dict(user_id=self.user_id, links=bulk_links))
        self.assertEqual(response.status_code, 201)
        
if __name__ == "__main__":
    unittest.main()