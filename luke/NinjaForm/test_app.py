import pytest
from NF import app, db, User, Thing  # Importing from your Flask app
from flask import url_for

@pytest.fixture
def client():
    """Setup a test client for the Flask app."""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # In-memory database for testing
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client  # This provides a fresh test client
        with app.app_context():
            db.drop_all()

def test_homepage(client):
    """Test if homepage loads successfully."""
    response = client.get("/")
    assert response.status_code == 200  # Ensure the homepage loads correctly

def test_create_user(client):
    """Test user creation through homepage form."""
    response = client.post("/", data={"name": "Alice"})
    assert response.status_code == 302  # Redirects to form page after successful creation

    # Check if the user exists in the database
    with app.app_context():
        user = User.query.filter_by(name="Alice").first()
        assert user is not None  # User should exist
        assert user.posts == 0

def test_create_thing(client):
    """Test adding a Thing for a user."""
    with app.app_context():
        user = User(name="TestUser", posts=0)
        db.session.add(user)
        db.session.commit()

    response = client.post(f"/form/{user.id}", data={"thing": "Dream", "rating": 5})
    assert response.status_code == 200  # Should not redirect, just reload the page

    with app.app_context():
        thing = Thing.query.filter_by(thing="Dream").first()
        assert thing is not None
        assert thing.rating == 5
        assert thing.user_id == user.id

def test_delete_thing(client):
    """Test deleting a Thing."""
    with app.app_context():
        user = User(name="TestUser", posts=0)
        db.session.add(user)
        db.session.commit()

        thing = Thing(thing="Dream", rating=5, user_id=user.id)
        db.session.add(thing)
        db.session.commit()
    
        assert Thing.query.count() == 1  # Ensure Thing was created

    response = client.get(f"/delete/{thing.id}/user")
    assert response.status_code == 302  # Redirect after deletion

    with app.app_context():
        assert Thing.query.count() == 0  # Ensure Thing is deleted
        user = User.query.get(user.id)
        assert user.posts == -1  # Since we decrement posts
