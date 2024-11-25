import sys
sys.path.append('backend/src')
import unittest
from flask_login import login_user
from models.user import User
from models.links import Link, db
from app import create_app, register_blueprints, register_extensions
import datetime
import uuid

from flask import current_app
import re

class LinkTestApp(unittest.TestCase):
    def setUp(self):
        self.flask_app=create_app()
        self.app=self.flask_app.test_client()
        
    def test_create_route(self):
        """Test the create link route of our app"""
        self.app.post('/auth/register',json=dict(email='test6@gmail.com',first_name='test6_first',last_name='test6_last',password='password6'))
        with self.app:
            self.app.post('/auth/login',json=dict(email='test6@gmail.com',password='password6'),follow_redirects=True)
            user=User.query.filter_by(email='test6@gmail.com').first()
            uid=user.id
            response=self.app.post('/links/create',query_string=dict(user_id=uid),json=dict(id=uuid.uuid4(),user_id=uid,long_url='https://google.com',title='Google',disabled=False,utm_source='test6_source',utm_medium='test6_medium',utm_campaign='test6_campaign',utm_term='test6_term',utm_content='test6_content',password_hash='link_password',expire_on=datetime.datetime(2022,11,25)), follow_redirects=True)
        assert response.status_code==201
    
    def test_link_route(self):
        """Test the get link route of our app"""
        self.app.post('/auth/register',json=dict(email='test7@gmail.com',first_name='test7_first',last_name='test7_last',password='password7'))
        with self.app:
            self.app.post('/auth/login',json=dict(email='test7@gmail.com',password='password7'),follow_redirects=True)
            user=User.query.filter_by(email='test7@gmail.com').first()
            uid=user.id
            self.app.post('/links/create',query_string=dict(user_id=uid),json=dict(user_id=uid,long_url='https://yahoo.in',title='Yahoo',disabled=False,utm_source='test6_source',utm_medium='test6_medium',utm_campaign='test6_campaign',utm_term='test6_term',utm_content='test6_content',password_hash='link_password',expire_on=datetime.datetime(2022,11,25)))
            link_id=Link.query.filter_by(long_url='https://yahoo.in').first().id
            response=self.app.get('/links/'+str(link_id))
        assert response.status_code==200
        
    def test_link_route_invalid(self):
        """Test the get link route of our app with an invalid id"""
        link_id=uuid.uuid4()
        response=self.app.get('/links/'+str(link_id))
        assert response.status_code==400
    
    def test_link_all_route(self):
        """Test the get all links route of our app"""
        self.app.post('/auth/register',json=dict(email='test8@gmail.com',first_name='test8_first',last_name='test8_last',password='password8'))
        with self.app:
            self.app.post('/auth/login',json=dict(email='test8@gmail.com',password='password8'))
            user=User.query.filter_by(email='test8@gmail.com').first()
            uid=user.id
            self.app.post('/links/create',query_string=dict(user_id=uid),json=dict(id=uuid.uuid4(),user_id=uid,long_url='https://google.in',title='Google2',disabled=False,utm_source='test6_source',utm_medium='test6_medium',utm_campaign='test6_campaign',utm_term='test6_term',utm_content='test6_content',password_hash='link_password',expire_on=datetime.datetime(2022,11,25)))
            self.app.post('/links/create',query_string=dict(user_id=uid),json=dict(id=uuid.uuid4(),user_id=uid,long_url='https://yahoo.com',title='Yahoo2',disabled=False,utm_source='test6_source',utm_medium='test6_medium',utm_campaign='test6_campaign',utm_term='test6_term',utm_content='test6_content',password_hash='link_password',expire_on=datetime.datetime(2022,11,25)))
            response=self.app.get('/links/all',query_string=dict(user_id=uid,localId=uid))
        assert response.status_code==200
        
    def test_link_update_route_valid(self):
        """Test the update link route of our app with a valid link id"""
        self.app.post('/auth/register',json=dict(email='test9@gmail.com',first_name='test9_first',last_name='test9_last',password='password9'))
        with self.app:
            self.app.post('/auth/login',json=dict(email='test9@gmail.com',password='password9'))
            user=User.query.filter_by(email='test9@gmail.com').first()
            uid=user.id
            self.app.post('/links/create',query_string=dict(user_id=uid),json=dict(user_id=uid,long_url='https://facebook.com',title='Facebook',disabled=False,utm_source='test6_source',utm_medium='test6_medium',utm_campaign='test6_campaign',utm_term='test6_term',utm_content='test6_content',password_hash='link_password',expire_on=datetime.datetime(2022,11,25)))
            link_id=Link.query.filter_by(long_url='https://facebook.com').first().id
            response=self.app.patch('/links/update/'+str(link_id),query_string=dict(user_id=uid),json=dict(id=link_id ,user_id=uid, stub='new_stub', long_url='new_long_url', title='new_title', disabled=False, utm_source='test6_source', utm_medium='test6_medium', utm_campaign='test6_campaign', utm_term='test6_term', utm_content='test6_content', password_hash='new_password', expire_on=datetime.datetime(2022,11,25)))
        assert response.status_code==201
   
    def test_link_update_route_invalid(self):
        """Test the update link route of our app with an invalid link id"""
        self.app.post('/auth/register',json=dict(email='test10@gmail.com',first_name='test10_first',last_name='test10_last',password='password10'))
        with self.app:
            self.app.post('/auth/login',json=dict(email='test10@gmail.com',password='password10'))
            user=User.query.filter_by(email='test10@gmail.com').first()
            uid=user.id
            link_id=uuid.uuid4()
            response=self.app.patch('/links/update/'+str(link_id),query_string=dict(user_id=uid),json=dict(id=link_id ,user_id=uid, stub='new_stub', long_url='new_long_url', title='new_title', disabled=False, utm_source='test6_source', utm_medium='test6_medium', utm_campaign='test6_campaign', utm_term='test6_term', utm_content='test6_content', password_hash='new_password', expire_on=datetime.datetime(2022,11,25)))
        assert response.status_code==400     
        
    
    def test_link_delete_route_valid(self):
        """Test the delete link route of our app with a valid link id"""
        self.app.post('/auth/register',json=dict(email='test11@gmail.com',first_name='test11_first',last_name='test11_last',password='password11'))
        with self.app:
            self.app.post('/auth/login',json=dict(email='test11@gmail.com',password='password11'))
            user=User.query.filter_by(email='test11@gmail.com').first()
            uid=user.id
            self.app.post('/links/create',query_string=dict(user_id=uid),json=dict(user_id=uid,long_url='https://facebook.in',title='Facebook2',disabled=False,utm_source='test6_source',utm_medium='test6_medium',utm_campaign='test6_campaign',utm_term='test6_term',utm_content='test6_content',password_hash='link_password',expire_on=datetime.datetime(2022,11,25)))
            link_id=Link.query.filter_by(long_url='https://facebook.in').first().id
            response=self.app.delete('/links/delete/'+str(link_id),query_string=dict(user_id=uid))
        assert response.status_code==200
    
    def test_link_stub_route_valid(self):
        """Test the stub route of our app, with a valid stub"""
        self.app.post('/auth/register',json=dict(email='test12@gmail.com',first_name='test12_first',last_name='test12_last',password='password12'))
        with self.app:
            self.app.post('/auth/login',json=dict(email='test12@gmail.com',password='password12'))
            user=User.query.filter_by(email='test12@gmail.com').first()
            uid=user.id
            self.app.post('/links/create',query_string=dict(user_id=uid),json=dict(user_id=uid,long_url='https://microsoft.com',title='Microsoft',disabled=False,utm_source='test6_source',utm_medium='test6_medium',utm_campaign='test6_campaign',utm_term='test6_term',utm_content='test6_content',password_hash='link_password',expire_on=datetime.datetime(2022,11,25)))
            stub=Link.query.filter_by(long_url='https://microsoft.com').first().stub
            response=self.app.get('/links/stub/'+str(stub))
        assert response.status_code==200
    
    
    def test_link_stub_route_invalid(self):
        """Test the stub route of our app, with a valid stub"""
        stub="test"
        response=self.app.get('/links/stub/'+str(stub))
        assert response.status_code==400
    
# Adding additional tests for custom url stub

class TestCustomStub(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up the Flask test app and database."""
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()
        register_blueprints(cls.app)
        register_extensions(cls.app)

    @classmethod
    def tearDownClass(cls):
        """Tear down the database and app context."""
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        """Set up a test client and initialize required data."""
        self.client = self.app.test_client()
        self.routes = ['login', 'home', 'signup']

    def validate_stub_string(self, stub):
        """Standalone validation for stubs."""
        valid_stub_regex = r'^[A-Za-z0-9\-_.~]*$'

        if len(stub) > 15:
            return True, "Stub length > 15"

        if len(stub) < 3:
            return True, "Stub length must be minimum of 3 characters"

        if not re.match(valid_stub_regex, stub):
            return True, "Stub contains invalid characters. Only A-Za-z0-9\-_.~ as allowed"

        return False, "Stub is valid!"

    def test_validate_stub_string(self):
        """Test cases for validate_stub_string function."""
        self.assertEqual(self.validate_stub_string("abc123"), (False, "Stub is valid!"))
        self.assertEqual(self.validate_stub_string(""), (True, "Stub length must be minimum of 3 characters"))
        self.assertEqual(self.validate_stub_string("a" * 16), (True, "Stub length > 15"))
        self.assertEqual(self.validate_stub_string("abc$123"), (True, "Stub contains invalid characters. Only A-Za-z0-9\-_.~ as allowed"))
        self.assertEqual(self.validate_stub_string("abc"), (False, "Stub is valid!"))
        self.assertEqual(self.validate_stub_string("a" * 15), (False, "Stub is valid!"))
        self.assertEqual(self.validate_stub_string("---"), (False, "Stub is valid!"))
        self.assertEqual(self.validate_stub_string("abc 123"), (True, "Stub contains invalid characters. Only A-Za-z0-9\-_.~ as allowed"))
        self.assertEqual(self.validate_stub_string("abc-._~123"), (False, "Stub is valid!"))

    def mock_check_stub_validity(self, stub):
        """Mock the check_stub_validity function."""
        # Mock reserved routes
        if stub in self.routes:
            return False, f"'{stub}' is a reserved route"

        # Mock existing database entries
        mock_db_stubs = ["shorty123"]
        if stub in mock_db_stubs:
            return False, "Stub is already taken"

        # Validate stub format
        return self.validate_stub_string(stub)

    def test_check_stub_validity(self):
        """Test cases for check_stub_validity function."""
        self.assertEqual(self.mock_check_stub_validity("login"), (False, "'login' is a reserved route"))
        self.assertEqual(self.mock_check_stub_validity("shorty123"), (False, "Stub is already taken"))
        self.assertEqual(self.mock_check_stub_validity("shorty"), (False, "Stub is valid!"))

    def test_verify_stub_boolean(self):
        """Test cases for verify_stub_boolean function."""
        self.assertFalse(self.mock_check_stub_validity("sho$rt")[0])
        self.assertTrue(self.mock_check_stub_validity("short")[0])
        self.assertFalse(self.mock_check_stub_validity("home")[0])
      
#if __name__=="__main__":
    #unittest.main()
