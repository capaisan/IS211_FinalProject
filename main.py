from flask import Flask, render_template, request, redirect, url_for, g, flash, session
import sqlite3
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm



app = Flask(__name__)
app.config['SECRET_KEY'] = 'asdfjkl;'



class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Check if the username and password are correct
        if form.username.data == 'admin' and form.password.data == 'password':
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html', form=form)

@app.route('/dashboard')
def dashboard():
    # Check if the user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))
    # Display the dashboard
    return render_template('dashboard.html')


def get_db():
    db = getattr(g, '_databse', None)
    if db is None:
        db = g._database = sqlite3.connect('posts.db', check_same_thread=False)
        db.execute('''CREATE TABLE IF NOT EXISTS posts
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    author TEXT NOT NULL,
                    published_date DATE NOT NULL)''')
        cursor = db.execute('SELECT id, title, content, author, published_date FROM posts ORDER BY published_date DESC')
        posts = cursor.fetchall()

    return posts


@app.route('/')
def homepage():
    data = get_db()
    return str(data)




if __name__ == "__main__":
    app.run(debug=True)