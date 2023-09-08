from flask import Flask, request, redirect, render_template, flash, url_for
from models import db, connect_db, User, Toddler, Word, ToddlerWord, WordArt, SuggestedWord
from flask_login import LoginManager, login_required, current_user, logout_user, login_user, UserMixin
from flask_debugtoolbar import DebugToolbarExtension
from forms import RegisterForm, LoginForm, AddToddlerForm, AddLearnedWordForm, SuggestWordForm
import requests
from flask_bcrypt import Bcrypt
from utilities import get_word_suggestion


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///tinytalk'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "secret"
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
@login_required
def dashboard():
    toddler = Toddler.query.filter_by(user_id=current_user.id).first()

    # Fetch the most recent learned word
    latest_word = None
    if toddler:
        latest_word = db.session.query(ToddlerWord, Word).join(Word).filter(ToddlerWord.toddler_id == toddler.id).order_by(ToddlerWord.learned_on.desc()).first()

    # Fetch the 4 latest suggested words
    latest_suggestions = None
    if toddler:
        latest_suggestions = db.session.query(SuggestedWord, Word).join(Word).filter(SuggestedWord.toddler_id == toddler.id).order_by(SuggestedWord.suggested_on.desc()).limit(4).all()

    return render_template('users/dashboard.html', toddler=toddler, latest_word=latest_word, latest_suggestions=latest_suggestions)



@app.route('/add_toddler', methods=['GET', 'POST'])
@login_required
def add_toddler():
    # Check if the user already has a toddler
    existing_toddler = Toddler.query.filter_by(user_id=current_user.id).first()
    if existing_toddler:
        flash('You have already added a toddler!')
        return redirect(url_for('dashboard'))

    form = AddToddlerForm()
    if form.validate_on_submit():
        new_toddler = Toddler(
        name=form.name.data, 
        age=form.age.data, 
        user_id=current_user.id, 
        image_url=form.image_url.data or None)
        db.session.add(new_toddler)

        words = [word.strip() for word in form.learned_words.data.split(',')]
        for word_text in words:
            word_instance = Word.query.filter_by(word=word_text).first()
            
            if not word_instance:
                word_instance = Word(word=word_text)
                db.session.add(word_instance)
            
            toddler_word = ToddlerWord(toddler=new_toddler, word=word_instance)
            db.session.add(toddler_word)
        
        db.session.commit()
        flash('Toddler added successfully!')
        return redirect(url_for('dashboard'))

    return render_template('toddlers/add_toddler.html', form=form)


@app.route('/suggest_word', methods=['GET', 'POST'])
@login_required
def suggest_word():
    form = SuggestWordForm()
    suggested_word_text = None
    
    if form.validate_on_submit():
        # Fetch word suggestion based on category
        category = form.category.data
        suggested_word_text = get_word_suggestion(category, current_user.id)
        
        if suggested_word_text:
            # Add this word to the SuggestedWord table
            word_instance = Word.query.filter_by(word=suggested_word_text).first()

            if not word_instance:
                word_instance = Word(word=suggested_word_text)
                db.session.add(word_instance)
                db.session.flush()  # to get id for the new word

            toddler = Toddler.query.filter_by(user_id=current_user.id).first()
            new_suggestion = SuggestedWord(toddler_id=toddler.id, word_id=word_instance.id)
            db.session.add(new_suggestion)
            db.session.commit()

            flash(f'Suggested word: {suggested_word_text}')
        else:
            flash('Unable to fetch a word suggestion. Try again later.')

    return render_template('words/suggest_word.html', form=form, word=suggested_word_text)



@app.route('/learned_words')
@login_required
def learned_words():
    toddler = Toddler.query.filter_by(user_id=current_user.id).first()
    learned_words = None
    if toddler:
        learned_words = db.session.query(ToddlerWord, Word).join(Word).filter(ToddlerWord.toddler_id == toddler.id).all()
    return render_template('words/learned_words.html', toddler=toddler, learned_words=learned_words)



@app.route('/submit_word', methods=['GET', 'POST'])
@login_required
def submit_word():
    form = AddLearnedWordForm()
    toddler = Toddler.query.filter_by(user_id=current_user.id).first()

    # Ensure that the user has a toddler registered
    if not toddler:
        flash('Please add a toddler first!')
        return redirect(url_for('add_toddler'))

    if form.validate_on_submit():
        words = [word.strip() for word in form.learned_words.data.split(',')]
        for word_text in words:
            word_instance = Word.query.filter_by(word=word_text).first()

            if not word_instance:
                word_instance = Word(word=word_text)
                db.session.add(word_instance)

            # Check if the word is already associated with the toddler
            exists = ToddlerWord.query.filter_by(toddler_id=toddler.id, word_id=word_instance.id).first()
            if not exists:
                toddler_word = ToddlerWord(toddler=toddler, word=word_instance)
                db.session.add(toddler_word)
            else:
                flash(f'Word "{word_text}" already associated with your toddler.', 'warning')
                
            # If there's a comment/note associated with the word
            if form.comment.data:
                word_instance.notes = form.comment.data

        db.session.commit()
        flash('Word(s) added successfully!')
        return redirect(url_for('dashboard'))

    return render_template('words/submit_word.html', form=form)


@app.route('/learn_word/<int:word_id>', methods=['POST'])
@login_required
def learn_word(word_id):
    word = Word.query.get(word_id)
    if word:
        toddler = Toddler.query.filter_by(user_id=current_user.id).first()
        toddler_word = ToddlerWord(toddler=toddler, word=word)
        db.session.add(toddler_word)

        # Update suggestion status
        suggestion = SuggestedWord.query.filter_by(toddler_id=toddler.id, word_id=word_id).first()
        if suggestion:
            suggestion.is_learned = True

        db.session.commit()
        flash(f'Learned word: {word.word}')
    return redirect(url_for('dashboard'))




@app.route('/delete_suggested_word/<int:suggestion_id>', methods=['POST'])
@login_required
def delete_suggested_word(suggestion_id):
    suggestion = SuggestedWord.query.get(suggestion_id)
    if suggestion:
        db.session.delete(suggestion)
        db.session.commit()
        flash('Suggested word deleted')
    return redirect(url_for('dashboard'))

@app.route('/suggested_words')
@login_required
def suggested_words():
    toddler = Toddler.query.filter_by(user_id=current_user.id).first()

    if toddler:
        suggested_words = db.session.query(SuggestedWord, Word).join(Word).filter(SuggestedWord.toddler_id == toddler.id).order_by(SuggestedWord.suggested_on.desc()).all()

        return render_template('users/suggested_words.html', toddler=toddler, suggested_words=suggested_words)

    return render_template('users/suggested_words.html', toddler=None, suggested_words=None)





