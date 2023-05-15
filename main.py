from flask import Flask, render_template, request, redirect, url_for, g, flash, session
import sqlite3
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm



app = Flask(__name__)
app.config['SECRET_KEY'] = 'asdfjkl;'
app.config['SESSION_TYPE'] = 'filesystem'


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == 'admin' and form.password.data == 'password':
            session['username'] = form.username.data  # Set the session after successful authentication
            return redirect(url_for('homepage'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html', form=form)

@app.route('/')
def homepage():
    if 'username' not in session:
        return redirect(url_for('login'))

    data = get_db()
    cursor = data.cursor()
    cursor.execute('SELECT id, title, content, author, published_date FROM posts ORDER BY published_date DESC')
    posts = cursor.fetchall()

    print(posts)

    return render_template('homepage.html', posts=posts)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('posts.db', check_same_thread=False)
        db.execute('''CREATE TABLE IF NOT EXISTS posts
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    author TEXT NOT NULL,
                    published_date DATE NOT NULL)''')
    return db



@app.route('/create_post', methods=['POST'])
def create_post():
    if 'username' not in session:
        return redirect(url_for('login'))

    title = request.form.get('title')
    content = request.form.get('content')
    author = request.form.get('author')

    db = get_db()
    db.execute('INSERT INTO posts (title, content, author, published_date) VALUES (?, ?, ?, datetime("now"))', (title, content, author))
    db.commit()

    return redirect(url_for('homepage'))


@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT * FROM posts WHERE id = ?', (post_id,))
    post = cursor.fetchone()

    if not post:
        flash('Post not found', 'error')
        return redirect(url_for('homepage'))

    if request.method == 'POST':
        updated_title = request.form.get('title')
        updated_content = request.form.get('content')

        cursor.execute('UPDATE posts SET title = ?, content = ? WHERE id = ?', (updated_title, updated_content, post_id))
        db.commit()

        flash('Post updated successfully', 'success')
        return redirect(url_for('homepage'))

    return render_template('edit_post.html', post=post)



@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()

    cursor.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    db.commit()

    flash('Post deleted successfully', 'success')
    return redirect(url_for('homepage'))



if __name__ == "__main__":
    app.run(debug=True)