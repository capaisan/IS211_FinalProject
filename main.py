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
        if form.username.data == 'admin' and form.password.data == 'password':
            return render_template('/homepage.html')
        else:
            flash('Invalid username or password', 'error')
    return render_template('/login.html', form=form)

@app.route('/')
def homepage():
    data = get_db()
    cursor = data.cursor()
    cursor.execute('SELECT id, title, content, author, published_date FROM posts ORDER BY published_date DESC')
    posts = cursor.fetchall()

    print(posts) #For debugging purposes, delete once solved.

    if 'username' not in session:
        return redirect('login')

    return render_template('/homepage.html', posts=posts)


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
        # cursor = db.execute('SELECT id, title, content, author, published_date FROM posts ORDER BY published_date DESC')
        # posts = cursor.fetchall()
        # return posts
    return db



@app.route('/create_post', methods=['POST'])
def create_post():
    # Get the data from the request
    title = request.form.get('title')
    content = request.form.get('content')
    author = request.form.get('author')

    # Insert the data into the database
    db = get_db()
    db.execute('INSERT INTO posts (title, content, author, published_date) VALUES (?, ?, ?, datetime("now"))', (title, content, author))
    db.commit()

    return render_template('homepage.html')



if __name__ == "__main__":
    app.run(debug=True)