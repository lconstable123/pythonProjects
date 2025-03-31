from app import app, db, login_manager
from flask import request, render_template, flash, redirect,url_for
from models import User, DinnerParty
from flask_login import current_user, login_user, logout_user, login_required
from forms import RegistrationForm,LoginForm, DinnerPartyForm, RsvpForm
#from urllib.parse import url_parse

# registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
  form = RegistrationForm()
  if form.validate_on_submit():
    user = User(username=form.username.data, email=form.email.data)
    user.set_password(form.password.data)
    db.session.add(user)
    db.session.commit()
  return render_template('register.html', title='Register', form=form)

# user loader
@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))

# login route
@app.route('/login', methods=['GET','POST'])
def login():
  form = LoginForm()
  if form.validate_on_submit():
    user = User.query.filter_by(email=form.email.data).first()
    if user and user.check_password(form.password.data):
      login_user(user, remember=form.remember.data)
      next_page = request.args.get('next')
      return redirect(url_for('user',username=user.username))
      #return redirect(next_page) if next_page else redirect(url_for('index', _external=True))
    else:
      return redirect(url_for('login', _external=True))
  return render_template('login.html', form=form)

# user route
@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
  user = User.query.filter_by(username=username).first_or_404()
  dinner_parties = DinnerParty.query.filter_by(party_host_id=user.id)
  if dinner_parties is None:
    dinner_parties = []
  form = DinnerPartyForm(csrf_enabled=False)
  if form.validate_on_submit():
    # update the values of each attribute to the corresponding form data here:
    new_dinner_party = DinnerParty(
      date = form.date.data,
      venue = form.venue.data,
      main_dish = form.main_dish.data,
      number_seats = int(form.number_seats.data), 
      party_host_id = user.id,
      attendees = username)
    db.session.add(new_dinner_party)
    db.session.commit()
  return render_template('user.html', user=user, dinner_parties=dinner_parties, form=form)

# rsvp route
@app.route('/user/<username>/rsvp/', methods=['GET', 'POST'])
@login_required
def rsvp(username):
  user = User.query.filter_by(username=username).first_or_404()
  dinner_parties = DinnerParty.query.all()
  if dinner_parties is None:
    dinner_parties = []
  form = RsvpForm(csrf_enabled=False)
  if form.validate_on_submit():
    # query the DinnerParty model here:
    dinner_party = DinnerParty.query.filter_by(id=int(form.party_id.data)).first()
    # update the attendees here:
    dinner_party.attendees += f", {username}"
    db.session.commit()
  return render_template('rsvp.html', user=user, dinner_parties=dinner_parties, form=form)

# landing page route
@app.route('/')
def index():
  # grab all guests and display them
  current_users = User.query.all()
  return render_template('landing_page.html', current_users = current_users)