import pytest

from flask import Flask
import os
os.system('cls')
os.environ['FLASK_ENV'] = 'testing'
from NF import app, db, User, Thing
# Setup a test client for the Flask application
@pytest.fixture
def client():
    # Set up the app for testing
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory'  # In-memory DB for tests
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Create tables for testing

            dummy_user = User(name="Test User", posts=0)
            db.session.add(dummy_user)
            db.session.commit()  # Commit the user to the database
            dummy_user1 = User(name="Test User1", posts=0)
            db.session.add(dummy_user1)
            dummy_thing = Thing(thing="Test Thing", rating=5, user_id=dummy_user.id)
            db.session.add(dummy_thing)
            dummy_thing2 = Thing(thing="Test Thing2", rating=5, user_id=dummy_user1.id)
            db.session.add(dummy_thing2)
            db.session.commit()  # Commit the thing to the database

        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()


# Test case for homepage (GET and POST)
def test_homepage_get(client):
    response = client.get('/')
    assert response.status_code == 200  # Check that the status code is 200 (OK)
    assert b"Dream App" in response.data  # Check if the main form is rendered


def test_homepage_user_inserted(client):
    user_data = {'name': 'luke'}
    response = client.post('/', data=user_data)
    redirected_response = client.get(response.headers['Location'])
    assert b"enter in a dream" in redirected_response.data  # Check that the form is rendered after the redirect

    with app.app_context():
        user = User.query.filter_by(name='luke').first()
        assert user is not None  # Ensure the user was added

def test_add_dream(client):
    dream_data = {'thing':'test dream 1','rating':2}
    response = client.post('/form/1', data = dream_data)

    with app.app_context():
        dream = Thing.query.filter_by(thing='test dream 1').first()
        assert dream is not None  # Ensure the dream was added
    redirected_response = client.get(response.headers['Location'])
    assert b"test dream 1" in redirected_response.data

    userId = dream.user_id
    #check to see if username is luke
    with app.app_context():
        user = User.query.filter_by(id = userId).first()
        assert user is not None # no user added for test dream 1
        assert user.name == 'Test User' #name is linled to Id
        assert user.posts == 1 ##count has been incremented
        assert len(user.things) > 0 # check backref to posts is population
        assert user.things[-1].thing == dream.thing # check to see if the backref to dream is equal
    #invalid field test
    dream_data = {'thing':'test dream 2','rating':''}
    response = client.post('/form/1', data = dream_data)

    with app.app_context():
        dream = Thing.query.filter_by(thing='test dream 2').first()
        assert dream is  None  # Ensure the invalid dream was not added
    assert b"test dream 2" not in redirected_response.data # Ensure the invalid dream was not rendered
     
with app.app_context():
    db.session.remove()
    db.drop_all()
    
