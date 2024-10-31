#
#MIT License
#
#Copyright (c) 2022 John Damilola, Leo Hsiang, Swarangi Gaurkar, Kritika Javali, Aaron Dias Barreto
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.



from operator import and_
from flask import Blueprint, jsonify,redirect                #import dependancies
from flask_cors import cross_origin
from string import ascii_letters, digits
from flask import request
from random import choice
try:
    from ..models.links import Link, db, load_link
    from ..models.links_anonymous import AnonymousLink
    from ..models.user import User, login_required2
    from ..models.engagements import Engagements
except ImportError:
    from models.links import Link, db, load_link
    from models.links_anonymous import AnonymousLink
    from models.user import User, login_required2
    from models.engagements import Engagements

links_bp = Blueprint(
    'links_bp', __name__
)

@links_bp.route('/links/<id>', methods = ['GET'])
@cross_origin(supports_credentials=True)
def getlink(id):
    '''This method is called when we want to fetch a single link, we pass link_id'''
    try:
        link = Link.query.get(id)
        return jsonify(
            link = link.to_json(),
            message = 'Fetched link successfully',
            status = 200
        ), 200
    except Exception as e:
        return jsonify(
            message = f"An error occurred: {e}",
            status = 400
        ), 400
        
@links_bp.route('/links/stub/<stub>', methods = ['GET'])
@cross_origin(supports_credentials=True)
def get_link_by_stub(stub):
    '''This method is called when we want to fetch a single link using the stub'''
    try:
        link = db.session.query(Link).filter(Link.stub==stub).first()
        return jsonify(
            link = link.to_json(),
            message = 'Fetched link successfully',
            status = 200
        ), 200
    except Exception as e:
        return jsonify(
            message = f"An error occurred: {e}",
            status = 400
        ), 400
        
@links_bp.route('/links_anonymous/stub/<stub>', methods = ['GET'])
@cross_origin(supports_credentials=True)
def get_anonymous_link_by_stub(stub):
    '''This method is called when we want to fetch a single link anonymously using the stub'''
    try:
        link = db.session.query(AnonymousLink).filter(AnonymousLink.stub==stub).first()
        return jsonify(
            link = link.to_json(),
            message = 'Fetched link successfully',
            status = 200
        ), 200
    except Exception as e:
        return jsonify(
            message = f"An error occurred: {e}",
            status = 400
        ), 400

@links_bp.route('/links/all', methods = ['GET'])
@login_required2()
@cross_origin(supports_credentials=True)
def getalllinks():
    '''This method is called when we want to fetch all of the links of a particular user. Here, we check if the user is authenticated, 
    if yes show all the links made by the user.'''
    args = request.args
    user_id = args and args['user_id']
    try:
        links = db.session.query(Link).join(User).filter(User.id==user_id).all()    
        _links = []
        for item in links:
            _links.append(item.to_json())
        return jsonify(
            links = _links,
            message = 'Fetching links successfully',
            status = 200
        ), 200
    except Exception as e:
        return jsonify(
            message = f"An error occurred {e}",
            status = 400
        ), 400

def create_shortlink():
    CHARS = ascii_letters + digits
    stub = "".join(choice(CHARS) for _ in range(12))
    
    return stub


@links_bp.route('/links/create', methods = ['POST'])
@login_required2()
@cross_origin(supports_credentials=True)
def create():
    '''This method is routed when the user requests to create a new link.'''
    args = request.args
    user_id = args and args['user_id']
    try:
        data = request.get_json()
        long_url=data['long_url']
        if data.get('stub'):
            stub=data.get('stub')
        else:
            stub=create_shortlink()
        title=data.get('title')
        disabled=data.get('disabled')
        utm_source=data.get('utm_source')
        utm_medium=data.get('utm_medium')
        utm_campaign=data.get('utm_campaign')
        utm_term=data.get('utm_term')
        utm_content=data.get('utm_content')
        password_hash=data.get('password_hash') 
        expire_on=data.get('expire_on')

        link = Link(user_id=user_id, stub=stub, long_url=long_url, title=title, disabled=disabled, utm_source=utm_source, utm_medium=utm_medium,utm_campaign=utm_campaign, utm_term=utm_term, utm_content=utm_content, password_hash=password_hash, expire_on=expire_on)
        link.user_id = user_id
        db.session.add(link)
        db.session.commit()

        return jsonify(
            link = link.to_json(),
            message = 'Create Link Successful',
            status = 201
        ), 201
    except Exception as e:
        return jsonify(
            message = f'Create Link Failed {e}',
            status = 400
        ), 400
        
@links_bp.route('/links/create_anonymous', methods = ['POST'])
@cross_origin(supports_credentials=True)
def create_anonymous():
    '''This method is routed when the user requests to create a new link anonymously.'''
    try:
        data = request.get_json()
        long_url=data['long_url']
        stub=create_shortlink()

        link = AnonymousLink(stub=stub, long_url=long_url)
        db.session.add(link)
        db.session.commit()

        return jsonify(
            link = link.to_json(),
            message = 'Create Link Successful',
            status = 201
        ), 201
    except Exception as e:
        return jsonify(
            message = f'Create Link Failed {e}',
            status = 400
        ), 400

@links_bp.route('/links/update/<id>', methods = ['PATCH'])
@login_required2()
@cross_origin(supports_credentials=True)
def update(id):
    '''This method is called when the user requests to update the link.'''
    try:
        request_data = request.get_json()
        data = {k: v for k, v in request_data.items() if v is not None}
        long_url=data['long_url']
        stub=data.get('stub')
        title=data.get('title')
        disabled=data.get('disabled')
        utm_source=data.get('utm_source')
        utm_medium=data.get('utm_medium')
        utm_campaign=data.get('utm_campaign')
        utm_term=data.get('utm_term')
        utm_content=data.get('utm_content')
        password_hash=data.get('password_hash') 
        expire_on=data.get('expire_on')

        link = load_link(id)
        if 'stub' in data:
            link.stub=stub
        if 'long_url' in data:
            link.long_url=long_url 
        if 'title' in data:
            link.title=title
        if 'disabled' in data:
            link.disabled=disabled
        if 'utm_source' in data:
            link.utm_source=utm_source
        if 'utm_medium' in data:
            link.utm_medium=utm_medium
        if 'utm_campaign' in data:
            link.utm_campaign=utm_campaign
        if 'utm_content' in data:
            link.utm_content=utm_content
        if 'utm_term' in data:
            link.utm_term=utm_term
        if 'password_hash' in data:
            link.password_hash=password_hash
        if 'expire_on' in data:
            link.expire_on=expire_on
        # db.session.query(Link).filter_by(id=id).update(stub=stub,long_url=long_url, title=title, disabled=disabled, utm_source=utm_source, utm_medium=utm_medium, utm_campaign=utm_campaign, utm_content=utm_content, utm_term=utm_term, password_hash=password_hash, expire_on=expire_on)
        # db.session.update()
        db.session.commit()

        return jsonify(
            link = link.to_json(),
            message = 'Update Link Successful',
            status = 201
        ), 201
    except Exception as e:
        return jsonify(
            message = f'Update Link Failed {e}',
            status = 400
        ), 400

@links_bp.route('/links/delete/<id>', methods = ['DELETE'])
@login_required2()
@cross_origin(supports_credentials=True)
def delete(id):
    '''This method is called when the user requests to delete the link. Only the link id is required to delete the deck.'''
    try:
        db.session.query(Link).filter_by(id=id).delete()
        db.session.commit()
        return jsonify(
            message = 'Delete link Successful',
            status = 200
        ), 200
    except Exception as e:
        return jsonify(
            message = f'Delete link Failed {e}',
            status = 400
        ), 400
    
    
@links_bp.route('/links/stats', methods = ['GET'])
@login_required2()
@cross_origin(supports_credentials=True)
def get_link_stats():
    '''This method is called when we want to fetch the stats of all the links of a particular user. Here, we check if the user is authenticated.'''
    args = request.args
    user_id = args and args['user_id']
    try:
        total_count = db.session.query(Link).join(User).filter(User.id==user_id).count()
        total_enabled = db.session.query(Link).join(User).filter(and_(User.id==user_id, Link.disabled==False)).count()
        total_disabled = db.session.query(Link).join(User).filter(and_(User.id==user_id, Link.disabled==True)).count()
        total_engagements = db.session.query(Engagements).join(Link).filter(Link.user_id==user_id).count()
         
        return jsonify(
            links = ({'total_count': total_count, 'total_enabled': total_enabled, 'total_disabled': total_disabled, 'total_engagements': total_engagements}),
            message = 'Fetching links successfully',
            status = 200
        ), 200
    except Exception as e:
        return jsonify(
            message = f"An error occurred {e}",
            status = 400
        ), 400
        
@links_bp.route('/links/<link_id>/engagements', methods = ['GET'])
@login_required2()
@cross_origin(supports_credentials=True)
def get_single_link_engagements(link_id):
    '''This method is routed when the user requests analytics for a single link.'''
    try:
        engagements = db.session.query(Engagements).join(Link).filter(Link.id==link_id).all()
        _engagements = []
        for item in engagements:
            _engagements.append(item.to_json())
        return jsonify(
            engagements = _engagements,
                message = 'Fetching Analytics data successfully',
                status = 200
            ), 200
    except Exception as e:
        return jsonify(
            links = [],
            message = f'Fetching Analytics failed {e}',
            status = 400
        ), 400

@links_bp.route('/links/engagements/<link_id>/create', methods = ['POST'])
@cross_origin(supports_credentials=True)
def create_engagement(link_id):
    '''This method is routed when the user requests to create a new engagement for a link.'''
    try:
        data = request.get_json()
        utm_source=data.get('utm_source')
        utm_medium=data.get('utm_medium')
        utm_campaign=data.get('utm_campaign')
        utm_term=data.get('utm_term')
        utm_content=data.get('utm_content')

        engagement = Engagements(link_id=link_id, utm_source=utm_source, utm_medium=utm_medium,utm_campaign=utm_campaign, utm_term=utm_term, utm_content=utm_content)
        db.session.add(engagement)
        db.session.commit()

        return jsonify(
            engagement = engagement.to_json(),
            message = 'Create Engagement Successful',
            status = 201
        ), 201
    except Exception as e:
        return jsonify(
            message = f'Create Engagement Failed {e}',
            status = 400
        ), 400

import random
import string

def create_unique_stub():
    """Generates a unique stub that does not already exist in the database."""
    while True:
        stub = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        # Check if this stub already exists in the database
        existing_stub = Link.query.filter_by(stub=stub).first()
        if not existing_stub:
            return stub


import json

@links_bp.route('/links/create_bulk', methods=['POST'])
@login_required2()
@cross_origin(supports_credentials=True)
def create_bulk():
    '''This method allows users to create multiple links in one request.'''
    user_id = request.args.get('user_id')
    print(user_id)
    try:
        data = request.get_json()
        # file = request.files.get('file')
        # if not file:
        #     return jsonify(message='No file provided', status=400), 400
        # data = json.load(file)
        print(data);
        # links_data = data['links']
        links_data = data.get('links', [])
        # print('linksssss',links_data);
        if not links_data:
            return jsonify(message='No links data found in the uploaded file', status=400), 400
        created_links = []

        for link_data in links_data:
            # Extract link details and set defaults
            long_url = link_data['long_url']
            print('url',long_url)
            stub = create_unique_stub()
            print('stub',stub)
            title = link_data.get('title')
            disabled = link_data.get('disabled', False)
            utm_source = link_data.get('utm_source')
            utm_medium = link_data.get('utm_medium')
            utm_campaign = link_data.get('utm_campaign')
            utm_term = link_data.get('utm_term')
            utm_content = link_data.get('utm_content')
            password_hash = link_data.get('password_hash') 
            expire_on = link_data.get('expire_on')

            if not long_url or not title:
                print('long url and title are required')
                return jsonify(message='Long URL and title are required for each link', status=400), 400
            
            # Create Link instance
            link = Link(
                user_id=user_id, stub=stub, long_url=long_url, title=title,
                disabled=disabled, utm_source=utm_source, utm_medium=utm_medium,
                utm_campaign=utm_campaign, utm_term=utm_term, utm_content=utm_content,
                password_hash=password_hash, expire_on=expire_on
            )
            print('------------------------')
            db.session.add(link)
            print('------------------------')
            created_links.append(link)
            print('------------------------')

        # Commit all links at once
        db.session.commit()
        
        # Return success with all created links' info
        return jsonify(
            links=[link.to_json() for link in created_links],
            message='Bulk link creation successful',
            status=201
        ), 201
        
    except Exception as e:
        return jsonify(
            message=f'Bulk link creation failed: {e}',
            status=400
        ), 400

@links_bp.route('/<stub>', methods=['GET'])
def redirect_stub(stub):
    """Redirects the short URL stub to its corresponding long URL."""
    try:
        # Look for the stub in the registered users' links
        link = Link.query.filter_by(stub=stub).first()

        if link:
            if link.disabled:
                return jsonify(message="This link has been disabled.", status=403), 403
            # elif link.max_visits and link.visit_count >= link.max_visits:
            #     # Automatically disable the link if it has reached the maximum number of visits
            #     link.disabled = True
            #     db.session.commit()
            #     return jsonify(message="This link has been disabled.", status=403), 403
            
            # Increment the visit count
            # link.visit_count += 1
            db.session.commit()
            return redirect(link.long_url)
        else:
            # Stub not found in user links, you might want to check in anonymous links
            anon_link = AnonymousLink.query.filter_by(stub=stub).first()
            if anon_link:
                return redirect(anon_link.long_url)
            else:
                return jsonify(message="Link not found.", status=404), 404
                
    except Exception as e:
        return jsonify(
            message=f"An error occurred: {e}",
            status=500
        ), 500