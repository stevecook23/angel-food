import os
import time
import secrets
from functools import wraps
from datetime import datetime, timedelta
from flask import (
    Flask, flash, render_template, redirect,
    request, session, url_for, abort
)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.utils import cloudinary_url


if os.path.exists("env.py"):
    import env


app = Flask(__name__)


# Configuration
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True


# Initialize extensions
mongo = PyMongo(app)
mail = Mail(app)


# Cloudinary configuration
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
    secure=True
)


# Decorator functions
def login_required(f):
    """Decorator to require login for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin privileges for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or session['user'] != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


# Routes
@app.route("/")
@app.route("/show_places")
def show_places():
    """Route to display all places."""
    places = mongo.db.places.find()
    return render_template("places.html", places=places)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Route for user registration."""
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        if existing_user:
            error_msg = "This account already exists. Please login."
            return render_template("register.html", error_msg=error_msg)

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "email": request.form.get("email").lower()
        }
        mongo.db.users.insert_one(register)

        session["user"] = request.form.get("username").lower()
        places = mongo.db.places.find()
        return render_template("places.html", places=places)
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Route for user login."""
    if request.method == "POST":
        username = request.form.get("username").lower()
        password = request.form.get("password")
        existing_user = mongo.db.users.find_one(
            {"username": username})

        if (existing_user and
                check_password_hash(existing_user["password"], password)):
            session["user"] = username
            places = mongo.db.places.find()
            return render_template(
                "places.html",
                places=places,
                username=username
            )
        elif existing_user:
            error_msg = "Incorrect username/password. Please try again."
            return render_template("login.html", error_msg=error_msg)
        else:
            error_msg = "Username not found. Please register if you're new."
            time.sleep(1)
            return render_template("register.html", error_msg=error_msg)

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Route for user logout."""
    session.pop("user", None)
    return render_template("login.html")


@app.route("/profile")
@login_required
def profile():
    """Route to display user profile."""
    username = session['user']
    user_places = list(mongo.db.places.find({'created_by': username}))
    return render_template(
        "profile.html", username=username, user_places=user_places)


@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    """Route for password reset request."""
    if request.method == "POST":
        email = request.form.get("email").lower()
        user = mongo.db.users.find_one({"email": email})
        if user:
            token = secrets.token_urlsafe(32)
            mongo.db.password_reset.insert_one({
                "email": email,
                "token": token,
                "expiry": datetime.utcnow() + timedelta(hours=1)
            })
            reset_link = url_for('reset_password', token=token, _external=True)
            send_reset_email(email, reset_link)
            return render_template("login.html")
        return "Email not found"
    return render_template("forgot.html")


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """Route to reset password."""
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


@app.route("/add_place", methods=['GET', 'POST'])
@login_required
def add_place():
    """Route to add a new place."""
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
                upload_result = cloudinary.uploader.upload(
                    file,
                    transformation=[
                        {'width': 500, 'height': 500, 'crop': 'fill'}
                    ])
                place["image_url"] = upload_result['secure_url']

        mongo.db.places.insert_one(place)
        return redirect(url_for("show_places"))

    cuisines = list(mongo.db.cuisine.find().sort("cuisine_name", 1))
    return render_template("add_place.html", cuisines=cuisines)


@app.route("/edit_place/<place_id>", methods=["GET", "POST"])
@login_required
def edit_place(place_id):
    """Route to edit an existing place."""
    place = mongo.db.places.find_one({"_id": ObjectId(place_id)})
    if not place or place['created_by'] != session['user']:
        abort(403)
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
                upload_result = cloudinary.uploader.upload(
                    file,
                    transformation=[
                        {'width': 500, 'height': 500, 'crop': 'fill'}
                    ])
                submit["image_url"] = upload_result['secure_url']

        mongo.db.places.update_one(
            {"_id": ObjectId(place_id)},
            {"$set": submit})
        return redirect(url_for("show_places"))
    return render_template("edit_place.html", place=place, cuisines=cuisines)


@app.route("/delete_place/<place_id>")
@login_required
def delete_place(place_id):
    """Route to delete a place."""
    place = mongo.db.places.find_one({"_id": ObjectId(place_id)})
    if not place or place['created_by'] != session['user']:
        abort(403)
    mongo.db.places.delete_one({"_id": ObjectId(place_id)})
    flash("Place Successfully Deleted")
    return redirect(url_for("show_places"))


@app.route("/get_cuisines")
@admin_required
def get_cuisines():
    """Route to display all cuisines."""
    cuisines = list(mongo.db.cuisine.find().sort("cuisine_name", 1))
    return render_template("cuisines.html", cuisines=cuisines)


@app.route("/add_cuisine", methods=["GET", "POST"])
@admin_required
def add_cuisine():
    """Route to add a new cuisine."""
    if request.method == "POST":
        cuisine = {
            "cuisine_name": request.form.get("cuisine_name")
        }
        mongo.db.cuisine.insert_one(cuisine)
        return redirect(url_for("get_cuisines"))

    return render_template("add_cuisine.html")


@app.route("/edit_cuisine/<cuisine_id>", methods=["GET", "POST"])
@admin_required
def edit_cuisine(cuisine_id):
    """Route to edit an existing cuisine."""
    if request.method == "POST":
        submit = {
            "$set": {
                "cuisine_name": request.form.get("cuisine_name")
            }
        }
        mongo.db.cuisine.update_one({"_id": ObjectId(cuisine_id)}, submit)
        return redirect(url_for("get_cuisines"))
    cuisine = mongo.db.cuisine.find_one({"_id": ObjectId(cuisine_id)})
    return render_template("edit_cuisine.html", cuisine=cuisine)


@app.route("/delete_cuisine/<cuisine_id>")
@admin_required
def delete_cuisine(cuisine_id):
    """Route to delete a cuisine."""
    mongo.db.cuisine.delete_one({"_id": ObjectId(cuisine_id)})
    return redirect(url_for("get_cuisines"))


@app.route('/search')
def search():
    """Route for search functionality."""
    query = request.args.get('query', '')
    results = list(search_places(query))
    return render_template('search_results.html', results=results, query=query)


# Helper functions
def send_reset_email(email, reset_link):
    """Send password reset email."""
    msg = Message(
        'Password Reset Request',
        sender='noreply@angelfood.com',
        recipients=[email]
    )
    msg.body = f"Click the following link to reset your password: {reset_link}"
    mail.send(msg)


def search_places(query):
    """Search for places in the database."""
    query = query.lower()
    return mongo.db.places.find({
        '$or': [
            {'place_name': {'$regex': query, '$options': 'i'}},
            {'review_headline': {'$regex': query, '$options': 'i'}}
        ]
    })


# Error handlers
@app.errorhandler(403)
def forbidden(e):
    """Handle 403 Forbidden error."""
    return render_template('403.html'), 403


# Template filters
@app.template_filter('cloudinary_url')
def cloudinary_url_filter(source, **kwargs):
    """Template filter for Cloudinary URLs."""
    return cloudinary_url(source, **kwargs)[0] if source else ''


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=False)
