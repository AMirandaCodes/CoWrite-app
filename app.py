import os

from flask import Flask, render_template, redirect, request, session, flash, url_for
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from helpers import login_required, sentence_count, word_count, line_count, paragraph_count
from sqlalchemy import desc

# Create the Flask app
app = Flask(__name__)

# Session configuration
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Profile pics
app.config["UPLOAD_FOLDER"] = "static/profile_pics"
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024 # 2 MB Max

# Database connection
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///cowrite.db"

from models import db, User, CoDraft, Contribution
db.init_app(app)

# Homepage
@app.route("/")
def index():
    return render_template("index.html")

# Page explaining what CoWrite is
@app.route("/how-it-works")
def how_it_works():
    return render_template("how_it_works.html")

# Form to create a new CoDraft
@app.route("/new-codraft", methods=["GET", "POST"])
@login_required
def new_codraft():
    # When form is submitted
    if request.method == "POST":
        title = request.form.get("title")
        category = request.form.get("category")
        unittype = request.form.get("unittype")
        text = request.form.get("text")
        try:
            maxcontribution = int(request.form.get("maxcontribution"))
        except ValueError:
            flash("Non-integer max. contribution.", "error")
            return redirect(url_for("new_codraft"))

        # Data validation
        if not title or not text or not category or not unittype:
            flash("Missing fields.", "error")
            return redirect(url_for("new_codraft"))

        if category=="default" or unittype=="default":
            flash("You can't use placeholder options.", "error")
            return redirect(url_for("new_codraft"))

        # Creates a new draft with the new contribution
        new_codraft = CoDraft(
            title=title,
            category=category,
            creator_id=session["user_id"],
            max_units=maxcontribution,
            max_unit_type=unittype
            )

        new_contribution = Contribution(
            codraft=new_codraft,
            author=User.query.get(session["user_id"]),
            text_snapshot=text
            )

        db.session.add(new_codraft)
        db.session.add(new_contribution)
        db.session.commit()

        flash("CoDraft created successfully!", "success")
        return redirect(url_for("codraft", id=new_codraft.id))

    else:
        # Page prior form submission
        return render_template("new_codraft.html")

# Displays all drafts the user has created or contributed on
@app.route("/my-codrafts")
@login_required
def my_codrafts():
    current_user = User.query.get(session["user_id"])

    # Gets all drafts created by the user
    created = (
        CoDraft.query
        .filter_by(creator_id=current_user.id)
        .order_by(desc(CoDraft.created_at))
        .all()
    )

    # Contributed drafts
    contributed = (
        Contribution.query
        .join(CoDraft)
        .filter(
            Contribution.user_id == current_user.id,
            CoDraft.creator_id != current_user.id
        )
        .distinct()
        .order_by(desc(Contribution.timestamp))
        .all()
        )

    return render_template(
        "my_codrafts.html",
        created=created,
        contributed=contributed
        )

# Details of a specific CoDraft
@app.route("/codraft/<int:id>")
def codraft(id):
    draft_info = CoDraft.query.get_or_404(id)

    # Gets all previous contributions
    contributions = (
        Contribution.query
        .filter_by(codraft_id=id)
        .order_by(desc(Contribution.timestamp))
        .all()
    )

    # Latest text (= text of last contribution)
    current_text = contributions[0].text_snapshot if contributions else ""

    return render_template(
        "codraft.html",
        info=draft_info,
        contributions=contributions,
        current_text=current_text
    )

# Add contribution
@app.route("/add-contribution/<int:id>", methods=["GET", "POST"])
@login_required
def add_contribution(id):
    draft_info = CoDraft.query.get_or_404(id)

    # Gets all previous contributions
    contributions = (
        Contribution.query
        .filter_by(codraft_id=id)
        .order_by(desc(Contribution.timestamp))
        .all()
    )

    # Latest text (= text of last contribution)
    current_text = contributions[0].text_snapshot if contributions else ""

    if request.method == "POST":
        # Either 'Add contribution' or 'Mark as complete'
        action = request.form.get("action")

        # New contribution
        if action == "contribute":
            # Checks draft is still open
            if draft_info.is_completed == True:
                flash("You can't contribute to a completed piece", "error")
                return redirect(url_for("codraft", id=id))

            # Gets text submitted
            new_text = request.form.get("contribution")
            if not new_text:
                flash("Contribution cannot be empty.", "error")
                return redirect(url_for("codraft", id=id))

            # Checks new text still keeps previous text
            if not new_text.strip().startswith(current_text.strip()):
                flash("Your contribution must keep the previous text.", "error")
                return redirect(url_for("codraft", id=id))

            # Checks contribution is below limit
            max_qty = draft_info.max_units
            max_type = draft_info.max_unit_type

            if max_type == "words":
                delta = word_count(new_text) - word_count(current_text)

                if delta <=0:
                    flash("To contribute, you must add new words.", "error")
                    return redirect(url_for("codraft", id=id))
                if delta > max_qty:
                    flash("You added more words than allowed.", "error")
                    return redirect(url_for("codraft", id=id))

            elif max_type == "sentences":
                delta = sentence_count(new_text) - sentence_count(current_text)

                if delta <=0:
                    flash("To contribute, you must add new sentence.", "error")
                    return redirect(url_for("codraft", id=id))
                if delta > max_qty:
                    flash("You added more sentences than allowed.", "error")
                    return redirect(url_for("codraft", id=id))

            elif max_type == "paragraphs":
                delta = paragraph_count(new_text) - paragraph_count(current_text)

                if delta <=0:
                    flash("To contribute, you must add new paragraphs.", "error")
                    return redirect(url_for("codraft", id=id))
                if delta > max_qty:
                    flash("You added more paragraphs than allowed.", "error")
                    return redirect(url_for("codraft", id=id))

            current_user = User.query.get(session["user_id"])

            new_contribution = Contribution(
                codraft=draft_info,
                author=current_user,
                text_snapshot=new_text
            )

            db.session.add(new_contribution)
            db.session.commit()

            flash("Contribution added successfully!", "success")
            return redirect(url_for("codraft", id=id))

        # Mark as complete
        elif action == "complete":
            if draft_info.creator_id != session["user_id"]:
                flash("You are not the creator of the piece.", "error")
                return redirect(url_for("codraft", id=id))
            else:
                draft_info.is_completed = True
                db.session.commit()

                flash("Marked as completed successfully!", "success")
                return redirect(url_for("codraft", id=id))

    else:
        # Page prior form submission
        return render_template(
        "add_contribution.html",
        info=draft_info,
        current_text=current_text,
    )

@app.route("/community")
def community():
    # Gets all drafts in database
    all_drafts = (
        CoDraft.query
        .order_by(desc(CoDraft.created_at))
        .all()
        )

    return render_template("community.html", drafts = all_drafts)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Missing fields.", "error")
            return redirect(url_for("login"))

        user = User.query.filter_by(username=username).first()

        if not user:
            flash("Invalid username or password.", "error")
            return redirect(url_for("login"))

        if not check_password_hash(user.password_hash, password):
            flash("Invalid username or password.", "error")
            return redirect(url_for("login"))

        session["user_id"] = user.id

        flash("Login successful!", "success")
        return redirect("/")

    else:
        # Page prior form submission
        return render_template("login.html")

# User profile
@app.route("/profile/<int:id>")
def profile(id):
    user = User.query.get_or_404(id)
    return render_template("profile.html", user=user)

# Change profile (only owner)
@app.route("/change-profile/<int:id>", methods=["GET", "POST"])
@login_required
def change_profile(id):
    user = User.query.get_or_404(id)

    # Checks user is profile owner
    if user.id != session["user_id"]:
        flash("You are not the profile owner!", "error")
        return redirect(url_for("profile", id=id))

    if request.method == "POST":
        file = request.files.get("profile_image")
        new_username = request.form.get("username")
        new_intro = request.form.get("intro")

        if file and file.filename != "":
            filename = secure_filename(file.filename)
            # Source: https://flask.palletsprojects.com/en/stable/patterns/fileuploads/
            os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)

            user.profile_image = filename

        # Checks if any changes were made at all
        if new_username == user.username and new_intro == user.intro and not file:
            flash("No changes were made.", "info")
            return redirect(url_for("profile", id=id))

        # Checks if a new username is already in database
        existing_user = User.query.filter_by(username=new_username).first()
        if existing_user and existing_user.id != user.id:
            flash("That username is not available.", "error")
            return redirect(url_for("change_profile", id=id))

        user.username = new_username
        user.intro = new_intro
        db.session.commit()

        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile", id=user.id))

    else:
        # Page prior form submission
        return render_template("change_profile.html", user=user)

@app.route("/register", methods=["GET", "POST"])
def register():
    # User submitting the register form
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password or not confirmation:
            flash("Missing fields", "error")
            return redirect("/register")

        if password != confirmation:
            flash("Passwords do not match.", "error")
            return redirect("/register")

        # Checks if username exists already
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already taken.", "error")
            return redirect("/register")

        # Create new user
        hashed_password = generate_password_hash(password)

        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        # Log user in
        session["user_id"] = new_user.id

        flash("Register successful!", "success")
        return redirect(url_for("index"))

    else:
        return render_template("register.html")


@app.route("/logout")
def logout():
    """Logout user"""
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    flash("Logout successful!", "info")
    return redirect(url_for("index"))

# Creates the table schema in the database
# Source: https://flask-sqlalchemy.readthedocs.io/en/stable/quickstart/
with app.app_context():
    db.create_all()
