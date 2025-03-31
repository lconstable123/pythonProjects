from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField,SubmitField
from wtforms.validators import DataRequired, NumberRange

#from NF import app

class ThingForm(FlaskForm):
    thing = StringField(label = "Thing: ", validators=[DataRequired()])
    rating = IntegerField(label ="Out of ten", validators=[DataRequired(),NumberRange(min=0,max=10, message="out of ten please")])
    submit = SubmitField("Add thing")

class SignUpForm(FlaskForm):
    name = StringField(label="Name",validators=[DataRequired()])
    submit = SubmitField("Add")


class AdminForm(FlaskForm):
    id = 1
    name = StringField(label = 'name', validators=[DataRequired()] )
    password = StringField(label = 'password', validators=[DataRequired()])
    submit = SubmitField("login")

