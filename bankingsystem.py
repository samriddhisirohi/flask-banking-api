from flask import Flask,jsonify,render_template,request
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
        transactions= db.relationship('Transaction', backref='account', lazy=True)


class Transaction(db.Model):
     txn_id= db.Column(db.Integer, primary_key=True)
     amount= db.Column(db.Float, nullable=False)
     txn_type= db.Column(db.String(10), nullable=False) # "deposit" or "withdrawal" or "transfer"
     timestamp= db.Column(db.DateTime, default=datetime.datetime.utcnow)
     #acc_id= db.Column(db.Integer, db.ForeignKey('account.acc_id'), nullable=False) #Foreign key linking to Account table
     sender_id = db.Column(
        db.Integer,
        db.ForeignKey("account.acc_id")
    )
     receiver_id = db.Column(
        db.Integer,
        db.ForeignKey("account.acc_id"))




with app.app_context():
    db.create_all()



#🧑 Create User API
@app.route("/create_user", methods=["GET","POST"])
def create_user():
  if request.method == "GET":
        return "Use POST to create user"
  
  data= request.get_json()
  new_user= User(name=data["name"])
  db.session.add(new_user)
  db.session.commit()
  return jsonify({"message": "User created"})



#🧾 Create Account API
@app.route("/create_account",methods=["POST"])
def create_account():
  data= request.get_json()
  account= Account(
    balance= data.get("balance",0.0), #default balance is 0.0 if not provided
    user_id= data["user_id"] #not .get() beacause user_id must be provided
  )
  db.session.add(account)
  db.session.commit()
  return jsonify({"message": "Account created"})



#💸 Transfer Money API
@app.route("/transfer", methods=["POST"])
def transfer():
    data= request.get_json()
    sender= Account.query.get(data["sender_id"]) #fetch sender account
    receiver= Account.query.get(data["receiver_id"])#fetch receiver account
    amount= data["amount"]

    if not sender:
        return jsonify({"error": "Sender not found"}), 404

    if not receiver:
        return jsonify({"error": "Receiver not found"}), 404

    if amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400

    if sender.balance < amount:
        return jsonify({"error": "Insufficient funds"}), 400
   
    #proper transaction handling with try-except to ensure atomicity
    try:
       sender.balance -= amount #deduct from sender
       receiver.balance +=amount #add to receiver

       transaction = Transaction(
            amount=amount,
            txn_type="transfer",
            sender_id=sender.id,
            receiver_id=receiver.id
        )
       db.session.add(transaction)
       db.session.commit()

    except Exception as e:
        db.session.rollback() #undo changes if error occurs
        return jsonify({"error": "Transaction failed"}), 500  
    
    return jsonify({"message": "Transfer Successful"})
    
if __name__ == "__main__":
    app.run(debug=True) #debug=True allows for easier development by providing detailed error messages and auto-reloading the server on code changes.
   
    
