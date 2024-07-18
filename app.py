import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import time
if os.path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")


mongo = PyMongo(app)


@app.route("/")
@app.route("/show_places")
def show_places():
    places = mongo.db.places.find()
    return render_template("places.html", places=places)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Checking if the username already exists
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        
        # Message if the username already exists
        if existing_user:
            return render_template("register.html")

        # Adding the new user
        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # Add the new user to the current session's cookie
        session["user"] = request.form.get("username").lower()
        places = mongo.db.places.find()
        return render_template("places.html", 
                                places = places)
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username").lower()
        password = request.form.get("password")
        
        existing_user = mongo.db.users.find_one({"username": username})

        if existing_user:
            if check_password_hash(existing_user["password"], password):
                session["user"] = username
                places = mongo.db.places.find()
                return render_template("places.html", places=places)
            else:
                error_msg = "Incorrect username/password. Please try again."
                return render_template("login.html", error_msg=error_msg)
        else:
            error_msg = "Username not found. Please register if you're new."
            time.sleep(1)  # Delay so the error message can be read
            return render_template("register.html", error_msg=error_msg)

    return render_template("login.html")


@app.route("/logout")
def logout():
    # Removes the user from the session cookie, logging them out
    session.pop("user")
    return render_template("login.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)