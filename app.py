import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_mail import Mail, Message
import time
import secrets
import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.utils import cloudinary_url
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


# Route for the Register a New User page
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
            "password": generate_password_hash(request.form.get("password")),
            "email": request.form.get("email").lower()
        }
        mongo.db.users.insert_one(register)

        # Add the new user to the current session's cookie
        session["user"] = request.form.get("username").lower()
        places = mongo.db.places.find()
        return render_template("places.html", 
                                places = places)
    return render_template("register.html")


# Route for the Login page
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
                return render_template("places.html", places=places, username=username)
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
    # Removes the user from the session cookie if logged in, logging them out
    if "user" in session:
        session.pop("user")
    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # Validate that the user is logged in and accessing their own profile
    if session.get("user") != username:
        return redirect(url_for("login"))

    # Fetch user details based on the username parameter
    user = mongo.db.users.find_one({"username": username})
    if not user:
        return "User not found", 404

    return render_template("profile.html", username=username)

# This section is for 'forgot my password'
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email").lower()
        user = mongo.db.users.find_one({"email": email})
        if user:
            # Generate a unique token
            token = secrets.token_urlsafe(32)
            # Store the token in the database with an expiration time
            mongo.db.password_reset.insert_one({
                "email": email,
                "token": token,
                "expiry": datetime.utcnow() + timedelta(hours=1)
            })
            # Send email with reset link
            reset_link = url_for('reset_password', token=token, _external=True)
            send_reset_email(email, reset_link)
            return render_template("login.html")
        return "Email not found"
    return render_template("forgot.html")

# Handles email-sending for forgot password
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

def send_reset_email(email, reset_link):
    msg = Message(
        'Password Reset Request',
        sender='noreply@angelfood.com',
        recipients=[email]
    )
    msg.body = f"Click the following link to reset your password: {reset_link}"
    mail.send(msg)

# Route to the Reset Password page
@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if request.method == "POST":
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        if password != confirm_password:
            return "Passwords do not match"
        
        reset_request = mongo.db.password_reset.find_one({
            "token": token,
            "expiry": {"$gt": datetime.utcnow()}
        })
        if not reset_request:
            return "Invalid or expired token"
        
        hashed_password = generate_password_hash(password)
        mongo.db.users.update_one(
            {"email": reset_request["email"]},
            {"$set": {"password": hashed_password}}
        )
        mongo.db.password_reset.delete_one({"token": token})
        return render_template("login.html")
    return render_template("reset_password.html")


# Route to the Add Place page
@app.route("/add_place", methods=['GET', 'POST'])
def add_place():
    if request.method == 'POST':
        takeaway = "on" if request.form.get("takeaway") else "off"
        place = {
            "cuisine_name": request.form.get("cuisine_name"),
            "place_name": request.form.get("place_name"),
            "review_headline": request.form.get("review_headline"),
            "review_text": request.form.get("review_text"),
            "takeaway": takeaway,
            "visited": request.form.get("visited"),
            "created_by": session["user"],
            "price_per": request.form.get("price_per")
        }

        if 'place_image' in request.files:
            file = request.files['place_image']
            if file:
                upload_result = cloudinary.uploader.upload(file, 
                    transformation=[
                        {'width': 500, 'height': 500, 'crop': 'fill'}
                    ])
                place["image_url"] = upload_result['secure_url']

        mongo.db.places.insert_one(place)
        return redirect(url_for("show_places"))

    cuisines = list(mongo.db.cuisine.find().sort("cuisine_name", 1))
    return render_template("add_place.html", cuisines=cuisines)


# Route to the Edit Place page
@app.route("/edit_place/<place_id>", methods=["GET", "POST"])
def edit_place(place_id):
    place = mongo.db.places.find_one({"_id": ObjectId(place_id)})
    cuisines = mongo.db.cuisine.find().sort("cuisine_name", 1)
    
    if request.method == 'POST':
        takeaway = "on" if request.form.get("takeaway") else "off"
        submit = {
            "cuisine_name": request.form.get("cuisine_name"),
            "place_name": request.form.get("place_name"),
            "review_headline": request.form.get("review_headline"),
            "review_text": request.form.get("review_text"),
            "takeaway": takeaway,
            "visited": request.form.get("visited"),
            "created_by": session["user"],
            "price_per": request.form.get("price_per")
        }

        if 'place_image' in request.files:
            file = request.files['place_image']
            if file:
                upload_result = cloudinary.uploader.upload(file, 
                    transformation=[
                        {'width': 500, 'height': 500, 'crop': 'fill'}
                    ])
                place["image_url"] = upload_result['secure_url']

        mongo.db.places.update_one({"_id": ObjectId(place_id)}, {"$set": submit})
        flash("Place Successfully Updated")
        return redirect(url_for("show_places"))
    
    return render_template("edit_place.html", place=place, cuisines=cuisines)


# Route to the Delete Place page
@app.route("/delete_place/<place_id>")
def delete_place(place_id):
    mongo.db.places.delete_one({"_id": ObjectId(place_id)})
    return redirect(url_for("show_places"))


# Cloudinary details
cloudinary.config(
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key = os.environ.get('CLOUDINARY_API_KEY'),
    api_secret = os.environ.get('CLOUDINARY_API_SECRET'),
    secure=True
)


# Cloudinary cropping to squares
@app.template_filter('cloudinary_url')
def cloudinary_url_filter(source, **kwargs):
    return cloudinary_url(source, **kwargs)[0] if source else ''
        

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)