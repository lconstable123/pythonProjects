import flask
from flask import Flask, render_template,request,url_for,redirect,flash
from routes import ThingForm, SignUpForm,AdminForm
from flask_sqlalchemy import SQLAlchemy
from models import *
from sqlalchemy.exc import IntegrityError
import os
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)


app.secret_key = 'your_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

#slaclhemy setup
if os.getenv('FLASK_ENV') == 'testing':
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'   # For testing only
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_database.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'you-will-never-guess'

class Admin(UserMixin):
    def __init__(self, id):
        self.id = id



#db = SQLAlchemy(app)
db.init_app(app)
  
@app.route('/', methods=["GET","POST"])
def homepage():
    userform = SignUpForm()
      
    if request.method == 'POST':
        try:
            user = User(name=userform.name.data, posts=0)
            db.session.add(user)
            db.session.commit()
            #flash("user added")
            things = Thing.query.all()    
            things_with_users = {thing.id: User.query.filter_by(id=thing.user_id).first()for thing in things}    
            users = User.query.all()
            return redirect(url_for('form',id=user.id))
        except IntegrityError as e:
            db.session.rollback() 
            flash("user adding error")  
    things = Thing.query.all()    
    things_with_users = {thing.id: User.query.filter_by(id=thing.user_id).first()for thing in things}    
    users = User.query.all()
    
    logged_in = current_user.is_authenticated
    
    return render_template('homepage.html',userList = users,form=userform,things = things, users=things_with_users)

@app.route('/form/<int:id>', methods=["GET","POST"])
def form(id):
    formId = id
    form = ThingForm()
    user = User.query.filter_by(id=formId).first()
    if request.method == 'POST' and form.thing.data is not None and form.rating.data is not None:
        try:
            newThing = Thing(thing=form.thing.data, rating = form.rating.data, user_id = id)
            db.session.add(newThing)
            user.posts = user.posts + 1
            db.session.commit()
            return redirect(url_for('form', id=id))  
        except ValueError:
            db.session.rollback() 
            flash("dream adding error")
    userPosts = user.things 
    return render_template('form.html',name=user.name, form = form, things = userPosts, postcount = user.posts)
    
@app.route('/delete/<int:id>/<string:page>')
def delete_item(id,page):
    formId = id
    item = Thing.query.filter_by(id=formId).first()
    user = User.query.filter_by(id=item.user_id).first()
    try:
        db.session.delete(item)
        user.posts = user.posts-1
        db.session.commit()
        
        #flash(page)
    except IndexError:
        db.session.rollback() 
        flash("dream delete error")
    if page == 'home':
        return redirect(url_for('homepage'))
    elif page == 'user':
        return redirect(url_for('form',id=user.id))
    else:
        return redirect(url_for('homepage'))


# @login_manager.user_loader
# def load_user(id):
#     return User.query.get(int(id))
@login_manager.user_loader
def load_user(user_id):
    return Admin(user_id)



@app.route('/admin',methods=['GET','POST'])
def admin():
    form = AdminForm()
    if flask.request.method == 'POST':

        hashName = generate_password_hash('luke')
        hashPass = generate_password_hash('admin')
        passOk = check_password_hash(hashPass,form.password.data)
        nameOk = check_password_hash(hashName,form.name.data)
        admin = Admin(id=1)
        if passOk and nameOk:
            flash("logged in sucessfully") 
            login_user(admin)
        else:
            flash("unsuccessful login")
    return render_template('admin.html', form=form)
    
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('homepage'))

@app.route('/secret')
@login_required
def secret():
    return f'''<H1>you did it</H1><a href="{url_for('homepage')}">back</a>'''


@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return f'''<p>bad login</p><a href="{url_for('homepage')}" style="color: blue;">back</a>'''

if __name__ == '__main__':
    app.run(debug=True)