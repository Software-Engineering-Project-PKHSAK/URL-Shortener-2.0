import re
from flask import current_app
import json
import uuid
import datetime
from backend.src.app import create_app, register_blueprints, register_extensions
from backend.src.models.links import Link, db
from backend.src.models.user import User
from flask_login import login_user
import unittest
import sys
from backend.src.routes.links import validate_stub_string, check_stub_validity, verify_stub_boolean

sys.path.append('backend/src')


class LinkTestApp(unittest.TestCase):
    def setUp(self):
        self.flask_app = create_app("testing")
        self.app = self.flask_app.test_client()
        with self.flask_app.app_context():
            db.create_all()

    def tearDown(self):
        with self.flask_app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_route(self):
        """Test the create link route of our app"""
        self.app.post('/auth/register', json=dict(email='test6@gmail.com',
                      first_name='test6_first', last_name='test6_last', password='password6'))
        with self.app:
            response = self.app.post(
                '/auth/login', json=dict(email='test6@gmail.com', password='password6'), follow_redirects=True)
            response_data = json.loads(response.data.decode('utf-8'))
            token = response_data.get("token")
            headers = {
                # Include the token in the Authorization header
                'Authorization': f'Bearer {token}'
            }
            user = User.query.filter_by(email='test6@gmail.com').first()
            uid = user.id
            response = self.app.post('/links/create',
                                     query_string=dict(user_id=uid),
                                     json=dict(
                                         id=uuid.uuid4(),
                                         user_id=uid,
                                         long_url='https://google.com',
                                         title='Google',
                                         disabled=False,
                                         utm_source='test6_source',
                                         utm_medium='test6_medium',
                                         utm_campaign='test6_campaign',
                                         utm_term='test6_term',
                                         utm_content='test6_content',
                                         password_hash='link_password',
                                         expire_on=datetime.datetime(2022, 11, 25)),
                                     headers=headers,
                                     follow_redirects=True)
        assert response.status_code == 201

    def test_link_route(self):
        """Test the get link route of our app"""
        self.app.post('/auth/register', json=dict(email='test7@gmail.com',
                      first_name='test7_first', last_name='test7_last', password='password7'))
        with self.app:
            response = self.app.post(
                '/auth/login', json=dict(email='test7@gmail.com', password='password7'), follow_redirects=True)
            response_data = json.loads(response.data.decode('utf-8'))
            token = response_data.get("token")
            headers = {
                # Include the token in the Authorization header
                'Authorization': f'Bearer {token}'
            }
            user = User.query.filter_by(email='test7@gmail.com').first()
            uid = user.id
            self.app.post('/links/create',
                          query_string=dict(user_id=uid),
                          json=dict(user_id=uid,
                                    long_url='https://yahoo.in',
                                    title='Yahoo',
                                    disabled=False,
                                    utm_source='test6_source',
                                    utm_medium='test6_medium',
                                    utm_campaign='test6_campaign',
                                    utm_term='test6_term',
                                    utm_content='test6_content',
                                    password_hash='link_password',
                                    expire_on=datetime.datetime(2022, 11, 25)
                                    ),
                          headers=headers
                          )
            link_id = Link.query.filter_by(
                long_url='https://yahoo.in').first().id
            response = self.app.get('/links/'+str(link_id))
        assert response.status_code == 200

    def test_link_route_invalid(self):
        """Test the get link route of our app with an invalid id"""
        link_id = uuid.uuid4()
        response = self.app.get('/links/'+str(link_id))
        assert response.status_code == 404

    def test_link_all_route(self):
        """Test the get all links route of our app"""
        self.app.post('/auth/register', json=dict(email='test8@gmail.com',
                      first_name='test8_first', last_name='test8_last', password='password8'))
        with self.app:
            response = self.app.post(
                '/auth/login', json=dict(email='test8@gmail.com', password='password8'))
            response_data = json.loads(response.data.decode('utf-8'))
            token = response_data.get("token")
            headers = {
                # Include the token in the Authorization header
                'Authorization': f'Bearer {token}'
            }
            user = User.query.filter_by(email='test8@gmail.com').first()
            uid = user.id
            self.app.post('/links/create', query_string=dict(user_id=uid), json=dict(id=uuid.uuid4(), user_id=uid, long_url='https://google.in', title='Google2', disabled=False, utm_source='test6_source',
                          utm_medium='test6_medium', utm_campaign='test6_campaign', utm_term='test6_term', utm_content='test6_content', password_hash='link_password', expire_on=datetime.datetime(2022, 11, 25)), headers=headers)
            self.app.post('/links/create', query_string=dict(user_id=uid), json=dict(id=uuid.uuid4(), user_id=uid, long_url='https://yahoo.com', title='Yahoo2', disabled=False, utm_source='test6_source',
                          utm_medium='test6_medium', utm_campaign='test6_campaign', utm_term='test6_term', utm_content='test6_content', password_hash='link_password', expire_on=datetime.datetime(2022, 11, 25)), headers=headers)
            response = self.app.get(
                '/links/all', query_string=dict(user_id=uid, localId=uid), headers=headers)
        assert response.status_code == 200

    def test_link_update_route_valid(self):
        """Test the update link route of our app with a valid link id"""
        self.app.post('/auth/register', json=dict(email='test9@gmail.com',
                      first_name='test9_first', last_name='test9_last', password='password9'))
        with self.app:
            response = self.app.post(
                '/auth/login', json=dict(email='test9@gmail.com', password='password9'))
            response_data = json.loads(response.data.decode('utf-8'))
            token = response_data.get("token")
            headers = {
                'Authorization': f'Bearer {token}'
            }
            user = User.query.filter_by(email='test9@gmail.com').first()
            uid = user.id
            self.app.post('/links/create', query_string=dict(user_id=uid), json=dict(user_id=uid, long_url='https://facebook.com', title='Facebook', disabled=False, utm_source='test6_source',
                          utm_medium='test6_medium', utm_campaign='test6_campaign', utm_term='test6_term', utm_content='test6_content', password_hash='link_password', expire_on=datetime.datetime(2022, 11, 25)), headers=headers)
            link_id = Link.query.filter_by(
                long_url='https://facebook.com').first().id
            response = self.app.patch('/links/update/'+str(link_id), query_string=dict(user_id=uid), json=dict(id=link_id, user_id=uid, stub='new_stub', long_url='new_long_url', title='new_title', disabled=False, utm_source='test6_source',
                                      utm_medium='test6_medium', utm_campaign='test6_campaign', utm_term='test6_term', utm_content='test6_content', password_hash='new_password', expire_on=datetime.datetime(2022, 11, 25)), headers=headers)
        assert response.status_code == 200

    def test_link_update_route_invalid(self):
        """Test the update link route of our app with an invalid link id"""
        self.app.post('/auth/register',json=dict(email='test10@gmail.com',first_name='test10_first',last_name='test10_last',password='password10'))
        with self.app:
            response = self.app.post('/auth/login',json=dict(email='test10@gmail.com',password='password10'))
            response_data = json.loads(response.data.decode('utf-8'))
            token = response_data.get("token")
            headers = {
                'Authorization': f'Bearer {token}'
            }
            user=User.query.filter_by(email='test10@gmail.com').first()
            uid=user.id
            link_id=uuid.uuid4()
            response=self.app.patch('/links/update/'+str(link_id),query_string=dict(user_id=uid),json=dict(id=link_id ,user_id=uid, stub='new_stub', long_url='new_long_url', title='new_title', disabled=False, utm_source='test6_source', utm_medium='test6_medium', utm_campaign='test6_campaign', utm_term='test6_term', utm_content='test6_content', password_hash='new_password', expire_on=datetime.datetime(2022,11,25)), headers=headers)
        assert response.status_code==404


    def test_link_delete_route_valid(self):
        """Test the delete link route of our app with a valid link id"""
        self.app.post('/auth/register',json=dict(email='test11@gmail.com',first_name='test11_first',last_name='test11_last',password='password11'))
        with self.app:
            response = self.app.post('/auth/login',json=dict(email='test11@gmail.com',password='password11'))
            response_data = json.loads(response.data.decode('utf-8'))
            token = response_data.get("token")
            headers = {
                'Authorization': f'Bearer {token}'
            }
            user=User.query.filter_by(email='test11@gmail.com').first()
            uid=user.id
            self.app.post('/links/create',query_string=dict(user_id=uid),json=dict(user_id=uid,long_url='https://facebook.in',title='Facebook2',disabled=False,utm_source='test6_source',utm_medium='test6_medium',utm_campaign='test6_campaign',utm_term='test6_term',utm_content='test6_content',password_hash='link_password',expire_on=datetime.datetime(2022,11,25)), headers=headers)
            link_id=Link.query.filter_by(long_url='https://facebook.in').first().id
            response=self.app.delete('/links/delete/'+str(link_id),query_string=dict(user_id=uid), headers=headers)
        assert response.status_code==200

    def test_link_stub_route_valid(self):
        """Test the stub route of our app, with a valid stub"""
        self.app.post('/auth/register',json=dict(email='test12@gmail.com',first_name='test12_first',last_name='test12_last',password='password12'))
        with self.app:
            response = self.app.post('/auth/login',json=dict(email='test12@gmail.com',password='password12'))
            response_data = json.loads(response.data.decode('utf-8'))
            token = response_data.get("token")
            headers = {
                'Authorization': f'Bearer {token}'
            }
            user=User.query.filter_by(email='test12@gmail.com').first()
            uid=user.id
            self.app.post('/links/create',query_string=dict(user_id=uid),json=dict(user_id=uid,long_url='https://microsoft.com',title='Microsoft',disabled=False,utm_source='test6_source',utm_medium='test6_medium',utm_campaign='test6_campaign',utm_term='test6_term',utm_content='test6_content',password_hash='link_password',expire_on=datetime.datetime(2022,11,25)), headers=headers)
            stub=Link.query.filter_by(long_url='https://microsoft.com').first().stub
            response=self.app.get('/links/stub/'+str(stub))
        assert response.status_code==200


    def test_link_stub_route_invalid(self):
        """Test the stub route of our app, with a valid stub"""
        stub="test"
        response=self.app.get('/links/stub/'+str(stub))
        assert response.status_code==404

# Adding additional tests for custom url stub

class TestCustomStub(unittest.TestCase):
    def setUp(self):
        self.flask_app = create_app("testing")
        self.app = self.flask_app.test_client()
        with self.flask_app.app_context():
            db.create_all()

    def tearDown(self):
        with self.flask_app.app_context():
            db.session.remove()
            db.drop_all()

    def test_validate_stub_string(self):
        """Test cases for validate_stub_string function."""
        self.assertEqual(validate_stub_string("abc123"), (False, "Stub is valid!"))
        self.assertEqual(validate_stub_string(""), (True, "Stub length must be minimum of 3 characters"))
        self.assertEqual(validate_stub_string("a" * 16), (True, "Stub length > 15"))
        self.assertEqual(validate_stub_string("abc$123"), (True, "Stub contains invalid characters. Only A-Za-z0-9\-_.~ as allowed"))
        self.assertEqual(validate_stub_string("abc"), (False, "Stub is valid!"))
        self.assertEqual(validate_stub_string("a" * 15), (False, "Stub is valid!"))
        self.assertEqual(validate_stub_string("---"), (False, "Stub is valid!"))
        self.assertEqual(validate_stub_string("abc 123"), (True, "Stub contains invalid characters. Only A-Za-z0-9\-_.~ as allowed"))
        self.assertEqual(validate_stub_string("abc-._~123"), (False, "Stub is valid!"))

    def test_check_stub_validity_reserved(self):
        """Reserved route test cases for check_stub_validity function."""
        with self.flask_app.app_context():
            self.assertEqual(check_stub_validity("login"), (False, "'login' is a reserved route"))
            self.assertEqual(check_stub_validity("links"), (False, "'links' is a reserved route"))
            self.assertEqual(check_stub_validity("create_bulk"), (False, "'create_bulk' is a reserved route"))
    
    def test_check_stub_validity_non_reserved(self):
        """Non reserved test cases for check_stub_validity function."""
        with self.flask_app.app_context():
            self.assertEqual(check_stub_validity("shorty123"), (True, "Stub is valid and available!"))
            self.assertEqual(check_stub_validity("shorty~_"), (True, "Stub is valid and available!"))

    def test_check_stub_validity_non_reserved_unavailable(self):
        """Non reserved but taken test cases for check_stub_validity function."""
        self.app.post('/auth/register', json=dict(email='test6@gmail.com',
                      first_name='test6_first', last_name='test6_last', password='password6'))
        with self.app:
            response = self.app.post(
                '/auth/login', json=dict(email='test6@gmail.com', password='password6'), follow_redirects=True)
            response_data = json.loads(response.data.decode('utf-8'))
            token = response_data.get("token")
            headers = {
                # Include the token in the Authorization header
                'Authorization': f'Bearer {token}'
            }
            user = User.query.filter_by(email='test6@gmail.com').first()
            uid = user.id
            self.app.post('/links/create',
                            query_string=dict(user_id=uid),
                            json=dict(
                                id=uuid.uuid4(),
                                user_id=uid,
                                long_url='https://google.com',
                                stub="google",
                                title='Google',
                                disabled=False,
                                utm_source='test6_source',
                                utm_medium='test6_medium',
                                utm_campaign='test6_campaign',
                                utm_term='test6_term',
                                utm_content='test6_content',
                                password_hash='link_password',
                                expire_on=datetime.datetime(2022, 11, 25)),
                            headers=headers,
                            follow_redirects=True)
            self.app.post('/links/create',
                query_string=dict(user_id=uid),
                json=dict(
                    id=uuid.uuid4(),
                    user_id=uid,
                    long_url='https://google.co.in',
                    stub="google2",
                    title='Google-in',
                    disabled=False,
                    utm_source='test6_source',
                    utm_medium='test6_medium',
                    utm_campaign='test6_campaign',
                    utm_term='test6_term',
                    utm_content='test6_content',
                    password_hash='link_password',
                    expire_on=datetime.datetime(2022, 11, 25)),
                headers=headers,
                follow_redirects=True)
        with self.flask_app.app_context():
            self.assertEqual(check_stub_validity("google"), (False, "Stub is already taken"))
            self.assertEqual(check_stub_validity("google2"), (False, "Stub is already taken"))

    def test_verify_stub_boolean(self):
        """Test cases for verify_stub_boolean function."""
        self.app.post('/auth/register', json=dict(email='test6@gmail.com',
                      first_name='test6_first', last_name='test6_last', password='password6'))
        with self.app:
            response = self.app.post(
                '/auth/login', json=dict(email='test6@gmail.com', password='password6'), follow_redirects=True)
            response_data = json.loads(response.data.decode('utf-8'))
            token = response_data.get("token")
            headers = {
                # Include the token in the Authorization header
                'Authorization': f'Bearer {token}'
            }
            user = User.query.filter_by(email='test6@gmail.com').first()
            uid = user.id
            self.app.post('/links/create',
                            query_string=dict(user_id=uid),
                            json=dict(
                                id=uuid.uuid4(),
                                user_id=uid,
                                long_url='https://google.com',
                                stub="short",
                                title='Google',
                                disabled=False,
                                utm_source='test6_source',
                                utm_medium='test6_medium',
                                utm_campaign='test6_campaign',
                                utm_term='test6_term',
                                utm_content='test6_content',
                                password_hash='link_password',
                                expire_on=datetime.datetime(2022, 11, 25)),
                            headers=headers,
                            follow_redirects=True)
        with self.flask_app.app_context():
            self.assertFalse(verify_stub_boolean("short"))
            self.assertTrue(verify_stub_boolean("home"))

    def test_valid_stub_with_special_characters(self):
        """Test a stub with all valid special characters."""
        stub = "-_.~"
        result = validate_stub_string(stub)
        self.assertEqual(result, (False, "Stub is valid!"))
    

# if __name__=="__main__":
    # unittest.main()
