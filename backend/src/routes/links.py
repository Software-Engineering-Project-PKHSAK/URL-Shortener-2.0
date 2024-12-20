import random
from operator import and_
from flask import g, Blueprint, jsonify, redirect, request, current_app
from flask_cors import cross_origin
from string import ascii_letters, digits
from enum import Enum, auto
from user_agents import parse as user_agent_parser
from ..models.links import Link, db, load_link
from ..models.links_anonymous import AnonymousLink
from ..models.user import User, token_required, token_required
from ..models.engagements import Engagements
import re as re

links_bp = Blueprint("links_bp", __name__)

class DeviceType(Enum):
    MOBILE = auto()
    TABLET = auto()
    DESKTOP = auto()

# Utility Functions
def create_stub(length=12):
    """Generates a random stub of specified length."""
    chars = ascii_letters + digits
    return "".join(random.choices(chars, k=length))

def validate_stub_string(stub: str) -> bool:
    # Define the regex pattern for a valid stub
    valid_stub_regex = r'^[A-Za-z0-9\-_.~]*$'
    
    # Check if stub is empty or exceeds 15 characters
    if len(stub) > 15:
        return tuple([True, "Stub length > 15"])
    
    if len(stub) < 3:
        return tuple([True, "Stub length must be minimum of 3 characters"])
    
    # Use regex to check if the stub contains only valid characters
    if not re.match(valid_stub_regex, stub):
        return tuple([True, "Stub contains invalid characters. Only A-Za-z0-9\-_.~ as allowed"])
    
    return tuple([False,"Stub is valid!"])


def check_stub_validity(stub):
    """Checks if the stub is valid and available."""
    # Get a list of routes
    routes = [rule.rule.strip("/").split("/") for rule in current_app.url_map.iter_rules()]
    
    # Flatten the list and remove duplicates
    routes_potentially_in_use = list(set([item for sublist in routes for item in sublist]))
    
    # Check if the stub matches any route
    if stub in routes_potentially_in_use:
        return False, f"'{stub}' is a reserved route"
    
    # Validate stub string format
    condition, message = validate_stub_string(stub)
    if condition:
        return False, message
    
    # Check if stub already exists in the database
    already_exists = db.session.query(db.exists().where(Link.stub == stub)).scalar()
    if already_exists:
        return False, "Stub is already taken"
    
    return True, "Stub is valid and available!"


def verify_stub_boolean(stub):
    """Checks if it's a valid stub string and returns a boolean."""
    is_valid, _ = check_stub_validity(stub)
    return is_valid


def create_unique_stub(length=6):
    """Generates a unique stub that doesn't exist in the database."""
    while True:
        stub = create_stub(length)
        if not Link.query.filter_by(stub=stub).first():
            return stub


def validate_link_data(data, require_all=False):
    """Validates link data for creation/update."""
    if require_all and not all(key in data for key in ["long_url", "title"]):
        return False, (
            jsonify(message="Long URL and title are required", status=400),
            400,
        )
    elif not require_all and not data.get("long_url"):
        return False, (jsonify(message="Long URL is required", status=400), 400)
    return True, None


def create_link_object(user_id, data, is_anonymous=False):
    """Creates a Link or AnonymousLink instance from data."""
    LinkClass = AnonymousLink if is_anonymous else Link
    link_data = {
        "stub": data.get("stub") if data.get("stub") and verify_stub_boolean(data.get("stub")) else create_unique_stub(),
        "long_url": data["long_url"],
    }

    if not is_anonymous:
        link_data.update(
            {
                "user_id": user_id,
                "title": data.get("title"),
                "disabled": data.get("disabled"),
                "utm_source": data.get("utm_source"),
                "utm_medium": data.get("utm_medium"),
                "utm_campaign": data.get("utm_campaign"),
                "utm_term": data.get("utm_term"),
                "utm_content": data.get("utm_content"),
                "password_hash": data.get("password_hash"),
                "expire_on": data.get("expire_on"),
                "max_visits": data.get("max_visits"),
                "tags": list(set(data.get("tags", []))),
                "ab_variants": data.get("ab_variants")
            }
        )

    return LinkClass(**link_data)


def update_link_attributes(link, data):
    """Updates link attributes if they exist in data."""
    updatable_fields = [
        "stub",
        "long_url",
        "title",
        "disabled",
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "utm_content",
        "utm_term",
        "password_hash",
        "expire_on",
        "max_visits",
        "tags"
    ]

    for field in updatable_fields:
        if field in data:
            if field == "tags":
                print(list(set(data[field])))
                setattr(link, field, list(set(data[field])))
            else:
                setattr(link, field, data[field])


def get_user_links(user_id):
    """Fetches all links for a given user."""
    return db.session.query(Link).join(User).filter(User.id == user_id).all()

def get_user_links_by_tags(user_id, tags):
    """Fetches all links for a given user by tags."""
    tag_conditions = [Link.tags.any(name=tag) for tag in tags]
    return db.session.query(Link).join(User).filter(
        and_(User.id == user_id, *tag_conditions)
    ).all()

def get_user_stats(user_id):
    """Fetches link statistics for a user."""
    return {
        "total_count": db.session.query(Link)
        .join(User)
        .filter(User.id == user_id)
        .count(),
        "total_enabled": db.session.query(Link)
        .join(User)
        .filter(and_(User.id == user_id, Link.disabled.is_(False)))
        .count(),
        "total_disabled": db.session.query(Link)
        .join(User)
        .filter(and_(User.id == user_id, Link.disabled.is_(True)))
        .count(),
        "total_engagements": db.session.query(Engagements)
        .join(Link)
        .filter(Link.user_id == user_id)
        .count(),
    }


def create_engagement(link_id, data):
    """Creates a new engagement record."""
    engagement = Engagements(
        link_id=link_id,
        utm_source=data.get("utm_source"),
        utm_medium=data.get("utm_medium"),
        utm_campaign=data.get("utm_campaign"),
        utm_term=data.get("utm_term"),
        utm_content=data.get("utm_content"),
        long_url=data.get("long_url") # Check this from front-end
    )
    db.session.add(engagement)
    return engagement

def create_engagement_from_link_and_user_agent(link, url_to_redirect_to, user_agent):
    """Creates a new engagement record from link and user agent."""
    ua_os, ua_browser, ua_device_type = get_device_properties(user_agent)
    engagement = Engagements(
        link_id = link.id,
        utm_source=link.utm_source,
        utm_medium=link.utm_medium,
        utm_campaign=link.utm_campaign,
        utm_term=link.utm_term,
        utm_content=link.utm_content,
        long_url = url_to_redirect_to,
        device_type = ua_device_type,
        device_os = ua_os,
        device_browser = ua_browser
    )
    db.session.add(engagement)
    return engagement

def get_device_properties(user_agent):
    ua_os = user_agent.os.family + ' ' + user_agent.os.version_string
    ua_browser = user_agent.browser.family + ' ' + user_agent.browser.version_string
    ua_device_type = None
    if user_agent.is_mobile:
        ua_device_type = DeviceType.MOBILE.name
    elif user_agent.is_tablet:
        ua_device_type = DeviceType.TABLET.name
    elif user_agent.is_pc:
        ua_device_type = DeviceType.DESKTOP.name

    return tuple([ua_os, ua_browser, ua_device_type])

def get_random_url_for_ab(link):
    """Returns a weighted random url based on ab variants provided"""
    ab_variants = link.ab_variants
    if ab_variants:
        urls = [item["url"] for item in ab_variants]
        percentages = [ (float((item["percentage"]))/100) if '.' in item["percentage"] else (int((item["percentage"]))/100) 
                        for item in ab_variants
                      ]
        urls.append(link.long_url)
        percentages.append(1-sum(percentages))
        print(link.long_url)
        print(urls, percentages)
        return random.choices(urls, percentages,k=1)[0]
    else:
        return link.long_url

# Route Handlers
@links_bp.route("/links/<id>", methods=["GET"])
@cross_origin(supports_credentials=True)
def get_link(id):
    """Fetches a single link by ID."""
    try:
        link = Link.query.get(id)
        if not link:
            return jsonify(message="Link not found", status=404), 404

        return jsonify(
            link=link.to_json(), message="Fetched link successfully", status=200
        ), 200
    except Exception as e:
        return jsonify(message=f"An error occurred: {str(e)}", status=400), 400

@links_bp.route("/links/<tags>", methods=["GET"])
@cross_origin(supports_credentials=True)
def get_link_by_tags(tags):
    """Fetches a links by tags."""
    try:
        user_id = request.args.get("user_id")
        if not user_id:
            return jsonify(message="User ID is required", status=400), 400
        links = get_user_links_by_tags(user_id, tags)
        return jsonify(
            links=[link.to_json() for link in links],
            message="Fetching links successfully",
            status=200,
        ), 200
    except Exception as e:
        return jsonify(message=f"An error occurred: {str(e)}", status=400), 400

@links_bp.route("/links/stub/<stub>", methods=["GET"])
@cross_origin(supports_credentials=True)
def get_link_by_stub(stub):
    """Fetches a single link using the stub."""
    try:
        link = db.session.query(Link).filter(Link.stub == stub).first()
        if not link:
            return jsonify(message="Link not found", status=404), 404

        return jsonify(
            link=link.to_json(), message="Fetched link successfully", status=200
        ), 200
    except Exception as e:
        return jsonify(message=f"An error occurred: {str(e)}", status=400), 400


@links_bp.route("/links_anonymous/stub/<stub>", methods=["GET"])
@cross_origin(supports_credentials=True)
def get_anonymous_link_by_stub(stub):
    """Fetches a single anonymous link using the stub."""
    try:
        link = (
            db.session.query(AnonymousLink).filter(AnonymousLink.stub == stub).first()
        )
        if not link:
            return jsonify(message="Link not found", status=404), 404

        return jsonify(
            link=link.to_json(), message="Fetched link successfully", status=200
        ), 200
    except Exception as e:
        return jsonify(message=f"An error occurred: {str(e)}", status=400), 400


@links_bp.route("/links/all", methods=["GET"])
@token_required()
@cross_origin(supports_credentials=True)
def get_all_links():
    """Fetches all links for an authenticated user."""
    try:
        if request.method == "OPTIONS":
            # Handle the preflight request
            return '', 204
        user_id = g.user.id
        if not user_id:
            return jsonify(message="User ID is required", status=400), 400

        links = get_user_links(user_id)
        return jsonify(
            links=[link.to_json() for link in links],
            message="Fetching links successfully",
            status=200,
        ), 200
    except Exception as e:
        return jsonify(message=f"An error occurred: {str(e)}", status=400), 400


@links_bp.route("/links/create", methods=["POST"])
@token_required()
@cross_origin(supports_credentials=True)
def create():
    """Creates a new link for an authenticated user."""
    try:
        user_id = g.user.id
        if not user_id:
            return jsonify(message="User ID is required", status=400), 400

        data = request.get_json()
        is_valid, error_response = validate_link_data(data)
        if not is_valid:
            return error_response

        link = create_link_object(user_id, data)
        db.session.add(link)
        db.session.commit()

        return jsonify(
            link=link.to_json(), message="Create Link Successful", status=201
        ), 201

    except Exception as e:
        db.session.rollback()
        return jsonify(message=f"Create Link Failed: {str(e)}", status=400), 400


@links_bp.route("/links/create_anonymous", methods=["POST"])
@cross_origin(supports_credentials=True)
def create_anonymous():
    """Creates an anonymous link."""
    try:
        data = request.get_json()
        is_valid, error_response = validate_link_data(data)
        if not is_valid:
            return error_response

        link = create_link_object(None, data, is_anonymous=True)
        db.session.add(link)
        db.session.commit()

        return jsonify(
            link=link.to_json(), message="Create Link Successful", status=201
        ), 201
    except Exception as e:
        db.session.rollback()
        return jsonify(message=f"Create Link Failed: {str(e)}", status=400), 400


@links_bp.route("/links/create_bulk", methods=["POST"])
@token_required()
@cross_origin(supports_credentials=True)
def create_bulk():
    """Creates multiple links in one request."""
    try:
        user_id = g.user.id
        if not user_id:
            return jsonify(message="User ID is required", status=400), 400

        links_data = request.get_json().get("links", [])
        if not links_data:
            return jsonify(message="No links data provided", status=400), 400

        created_links = []
        for data in links_data:
            is_valid, error_response = validate_link_data(data, require_all=True)
            if not is_valid:
                return error_response

            link = create_link_object(user_id, data)
            db.session.add(link)
            created_links.append(link)

        db.session.commit()
        return jsonify(
            links=[link.to_json() for link in created_links],
            message="Bulk link creation successful",
            status=201,
        ), 201

    except Exception as e:
        db.session.rollback()
        return jsonify(message=f"Bulk link creation failed: {str(e)}", status=400), 400


@links_bp.route("/links/update/<id>", methods=["PATCH"])
@token_required()
@cross_origin(supports_credentials=True)
def update(id):
    """Updates an existing link."""
    try:
        data = {k: v for k, v in request.get_json().items() if v is not None}
        if not data:
            return jsonify(message="No update data provided", status=400), 400

        link = load_link(id)
        if not link:
            return jsonify(message="Link not found", status=404), 404

        update_link_attributes(link, data)
        db.session.commit()

        return jsonify(
            link=link.to_json(), message="Update Link Successful", status=200
        ), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(message=f"Update Link Failed: {str(e)}", status=400), 400


@links_bp.route("/links/delete/<id>", methods=["DELETE"])
@token_required()
@cross_origin(supports_credentials=True)
def delete(id):
    """Deletes a link."""
    try:
        db.session.query(Link).filter_by(id=id).delete()
        db.session.commit()
        return jsonify(message="Delete link Successful", status=200), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(message=f"Delete link Failed: {str(e)}", status=400), 400


@links_bp.route("/links/stats", methods=["GET"])
@token_required()
@cross_origin(supports_credentials=True)
def get_link_stats():
    """Fetches link statistics for an authenticated user."""
    try:
        user_id = g.user.id
        if not user_id:
            return jsonify(message="User ID is required", status=400), 400

        stats = get_user_stats(user_id)
        return jsonify(
            links=stats, message="Fetching links successfully", status=200
        ), 200
    except Exception as e:
        return jsonify(message=f"An error occurred: {str(e)}", status=400), 400


@links_bp.route("/links/<link_id>/engagements", methods=["GET"])
@token_required()
@cross_origin(supports_credentials=True)
def get_single_link_engagements(link_id):
    """Fetches engagement data for a single link."""
    try:
        engagements = (
            db.session.query(Engagements).join(Link).filter(Link.id == link_id).all()
        )
        return jsonify(
            engagements=[engagement.to_json() for engagement in engagements],
            message="Fetching Analytics data successfully",
            status=200,
        ), 200
    except Exception as e:
        return jsonify(message=f"Fetching Analytics failed: {str(e)}", status=400), 400


@links_bp.route("/links/engagements/<link_id>/create", methods=["POST"])
@cross_origin(supports_credentials=True)
def create_engagement_route(link_id):
    """Creates a new engagement record for a link."""
    try:
        data = request.get_json()
        engagement = create_engagement(link_id, data)
        db.session.commit()

        return jsonify(
            engagement=engagement.to_json(),
            message="Create Engagement Successful",
            status=201,
        ), 201
    except Exception as e:
        db.session.rollback()
        return jsonify(message=f"Create Engagement Failed: {str(e)}", status=400), 400

@links_bp.route('/verify/<stub>', methods=['GET'])
def verify_stub(stub):
    """Checks if it's a valid stub string and returns a response."""
    is_valid, message = check_stub_validity(stub)
    status = 200 if is_valid else 400
    return jsonify(message=message, status=status), status

@links_bp.route("/<stub>", methods=["GET"])
def redirect_stub(stub):
    """Redirects short URL to its corresponding long URL."""
    try:
        link = Link.query.filter_by(stub=stub).first()
        if link:
            if link.disabled:
                return jsonify(message="This link has been disabled.", status=403), 403
            elif link.max_visits and link.visit_count >= link.max_visits:
                link.disabled = True
                db.session.commit()
                return jsonify(message="This link has been disabled.", status=403), 403

            url_to_redirect_to = link.long_url
            if link.ab_variants is not None and len(link.ab_variants) > 0:
                url_to_redirect_to = get_random_url_for_ab(link)

            user_agent = user_agent_parser(request.headers.get("User-Agent"))
            create_engagement_from_link_and_user_agent(link, url_to_redirect_to, user_agent)
            link.visit_count += 1
            db.session.commit()
            
            if not url_to_redirect_to.startswith(("http://", "https://")):
                url_to_redirect_to = "https://" + url_to_redirect_to

            # If requested through frontend/a/{stub}, return JSON for front-end landing page,
            # else redirect directly to long-url
            referrer_url = request.headers.get("Origin")
            if referrer_url is not None and "http://localhost:3000" in referrer_url:
                return jsonify(
                    link=link.to_json(), status=200
                ), 200
            else:
                return redirect(url_to_redirect_to)

        # Check anonymous links if not found in regular links
        anon_link = AnonymousLink.query.filter_by(stub=stub).first()
        if anon_link:
            return redirect(anon_link.long_url)

        return jsonify(message="Link not found.", status=404), 404

    except Exception as e:
        return jsonify(message=f"An error occurred: {str(e)}", status=500), 500
