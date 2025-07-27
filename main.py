import os
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)
app.secret_key = 'e4c2d50a1fa64b31c1b57ed2df6a97d8'


UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database init
def init_db():
    with sqlite3.connect('blog.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                image TEXT,
                video TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        # Default admin
        cursor = conn.execute("SELECT * FROM admin")
        if not cursor.fetchall():
            conn.execute("INSERT INTO admin (username, password) VALUES (?, ?)", ('admin', 'password'))

# Home page
@app.route('/')
def index():
    conn = sqlite3.connect('blog.db')
    posts = conn.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('blog.db')
        user = conn.execute("SELECT * FROM admin WHERE username=? AND password=?", (username, password)).fetchone()
        conn.close()
        if user:
            session['admin'] = True
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

# Dashboard
@app.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect(url_for('login'))
    conn = sqlite3.connect('blog.db')
    posts = conn.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('dashboard.html', posts=posts)

# Add Post
@app.route('/post', methods=['GET', 'POST'])
def post():
    if not session.get('admin'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        video = request.form['video']

        image_file = request.files['image']
        image_path = None
        if image_file:
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            image_path = image_path.replace('static/', '')

        conn = sqlite3.connect('blog.db')
        conn.execute("INSERT INTO posts (title, content, image, video) VALUES (?, ?, ?, ?)",
                     (title, content, image_path, video))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template('post.html')

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
