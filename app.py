from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User
from sqlalchemy.exc import IntegrityError
from forms import RegisterUser

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
            return render_template('resgister.html', form=form)
        session['user_id'] = new_user.id
        flash('Welcome! Succesfully Created Your Account!')
        return redirect('/secret')

    return render_template("register.html", form=form)
