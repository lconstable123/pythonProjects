from flask_sqlalchemy import SQLAlchemy

# Initialize db (don't need to initialize again if you import app and db)
db = SQLAlchemy()

class Thing(db.Model):
    id = db.Column(db.Integer,primary_key= True)
    thing = db.Column(db.String, index = True, unique = False)
    rating = db.Column(db.Integer, index = True, unique = False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

    def __repr__(self):
        return f"{self.thing}"

class User(db.Model):
    id = db.Column(db.Integer,primary_key= True)
    name = db.Column(db.String, index = True, unique = True)
    posts = db.Column(db.Integer, index = True, unique = False)
    things = db.relationship('Thing', backref='owner', lazy=True)


    def __repr__(self):
        return f"{self.name}"
       

