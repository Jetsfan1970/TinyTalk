from flask import Flask, request, redirect, render_template, flash, url_for
from models import db, connect_db, User, Toddler, Word, ToddlerWord, WordArt
from flask_login import LoginManager, login_required, current_user, logout_user, login_user, UserMixin
from flask_debugtoolbar import DebugToolbarExtension
from forms import RegisterForm, LoginForm, AddToddlerForm
import requests
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///tinytalk'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "dc2b223fffdfc3eefc14b6aafefb710ed97c4f002618648dd56c5c309a547c8b"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)

connect_db(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
bcrypt = Bcrypt(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
# add in method [GET] and [POST] to auth
def homepage():
    return render_template('users/home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))


        # If the password check fails, you might want to flash an error message
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')

    return render_template('users/login.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(email=form.email.data, username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
        
    return render_template('users/register.html', form=form)


@app.route('/dashboard')
def dashboard():
    return render_template('users/dashboard.html')

@app.route('/add_toddler', methods=['GET','POST'])
@login_required
def add_toddler():
    form = AddToddlerForm()
    if form.validate_on_submit():
        # First, create and add the toddler.
        new_toddler = Toddler(name=form.name.data, age=form.age.data, user_id=current_user.id)
        db.session.add(new_toddler)

        # Splitting entered words and associating them with the toddler.
        words = [word.strip() for word in form.learned_words.data.split(',')]
        for word_text in words:
            word_instance = Word.query.filter_by(word=word_text).first()
            
            # If the word doesn't exist in the database, create it.
            if not word_instance:
                word_instance = Word(word=word_text)
                db.session.add(word_instance)
            
            # Create an association between the word and the toddler.
            toddler_word = ToddlerWord(toddler=new_toddler, word=word_instance)
            db.session.add(toddler_word)
        
        db.session.commit()
        flash('Toddler added successfully!')
        return redirect(url_for('dashboard'))  # or whichever route you want to redirect to

    return render_template('toddlers/add_toddler.html', form=form)

@app.route('/view_toddlers')
def view_toddler():
    return render_template('toddlers/view_toddler.html')

@app.route('/suggest_words')
def get_new_words():
    return render_template('words/suggest_words')

@app.route('/learned_words')
def learned_words():
    return render_template('words/learned_words.html')

@app.route('/submit_word')
def submit_word():
    return render_template('words/submit_word.html')


