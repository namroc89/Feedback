from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from sqlalchemy.exc import IntegrityError
from forms import RegisterUser, LogInUser, FeedbackForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///feedback_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)


toolbar = DebugToolbarExtension(app)


@app.route('/')
def hhome_page():
    """page that redirects users to the register page"""
    return redirect('/register')


@app.route('/register', methods=['POST', 'GET'])
def register_user():
    """Shows form to create User and adds User to the database"""
    form = RegisterUser()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(
            username, password, email, first_name, last_name)

        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken. Please pick another')
            return render_template('register.html', form=form)
        session['user_id'] = new_user.id
        flash('Welcome! Succesfully Created Your Account!')
        return redirect(f'/user/{new_user.username}')

    return render_template("register.html", form=form)


@app.route('/login', methods=['POST', 'GET'])
def show_login():
    """takes user to page to log in"""
    form = LogInUser()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}!")
            session['user_id'] = user.id
            return redirect(f'/user/{user.username}')
        else:
            form.username.errors = ['Invalid username/passord.']
    return render_template('login.html', form=form)


@app.route('/user/<username>')
def show_secret(username):
    if "user_id" not in session:
        flash("You must be logged in for that.")
        return redirect('/login')
    user = User.query.filter_by(username=username).first()

    return render_template('user_details.html', user=user)


@app.route('/user/<username>/delete', methods=['POST'])
def delete_user(username):
    """deletes selected user"""
    user = User.query.filter_by(username=username).first()
    if user.id == session['user_id']:
        db.session.delete(user)
        db.session.commit()
        flash("User Deleted")
        return redirect('/login')
    flash("You don't have persmission to do that!")
    return redirect('/login')


@app.route('/user/<username>/feedback/add', methods=['GET', 'POST'])
def show_feedback_form(username):
    """Shows form if user is logged in"""
    if "user_id" not in session:
        flash("Must be logged in")
        return redirect("/login")
    user = User.query.filter_by(username=username).first()
    form = FeedbackForm()
    if user.id != session['user_id']:
        flash("Incorrect user")
        return redirect("/login")
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        new_feedback = Feedback(
            title=title, content=content, username=user.username)
        db.session.add(new_feedback)
        db.session.commit()
        return redirect(f'/user/{user.username}')

    return render_template('add_feedback.html', form=form, user=user)


@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_post(feedback_id):
    """delete selected post"""
    if 'user_id' not in session:
        flash("Please login first!")
        return redirect('/login')
    post = Feedback.query.get_or_404(feedback_id)
    if post.user.id == session['user_id']:
        db.session.delete(post)
        db.session.commit()
        flash("Post deleted!")
        return redirect(f'/user/{post.user.username}')
    flash("You don't have permission to do that!")
    return redirect('/login')


@app.route('/feedback/<int:feedback_id>/update', methods=['POST', 'GET'])
def edit_post(feedback_id):
    """edit post"""
    if 'user_id' not in session:
        flash("Please login first!")
        return redirect('/login')
    post = Feedback.query.get_or_404(feedback_id)
    form = FeedbackForm(obj=post)
    if post.user.id == session['user_id']:
        if form.validate_on_submit():
            post.title = form.title.data
            post.content = form.content.data
            db.session.commit()
            return redirect(f'/user/{post.user.username}')
    return render_template("edit_post.html", form=form, post=post)


@app.route('/logout')
def logout():
    """logs user out and redirects home"""
    session.pop("user_id")

    return redirect('/')
