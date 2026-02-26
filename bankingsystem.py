from flask import Flask,jsonify,sqlalchemy,render_template,request
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)   # 👈 This must come BEFORE any @app.route

class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///bank.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

db = SQLAlchemy()

class User(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(100), nullable=False)
    accounts= db.relationship('Account', backref='user', lazy=True)
    #One user → Many accounts
    #backref="user" lets Account access its user
    #lazy=True loads data when needed

class Account(db.Model):
        acc_id = db.Column(
        db.Integer,
        db.Sequence('acc_id_seq', start=101),
        primary_key=True
    )
        balance= db.Column(db.Float, nullable=False, default=0.0)
        user_id= db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) #Foreign key linking to User table
        transactions= db.relationship('Transaction', backref='account', lazy=True)#