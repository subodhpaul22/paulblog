from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3, os

app = Flask(__name__)
app.secret_key = 'supersecret'  # change it

DB = 'blog.db'

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
init_db()

@app.route('/')
def index():
    with sqlite3.connect(DB) as conn:
        posts = conn.execute('SELECT * FROM posts ORDER BY created_at DESC').fetchall()
    return render_template('index.html', posts=posts)

@app.route('/post/<int:post_id>')
def view_post(post_id):
    with sqlite3.connect(DB) as conn:
        post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    return render_template('post.html', post=post)

# Admin Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == '1234':
            session['admin'] = True
            return redirect('/dashboard')
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'admin' not in session:
        return redirect('/login')
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        with sqlite3.connect(DB) as conn:
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content))
        return redirect('/dashboard')
    with sqlite3.connect(DB) as conn:
        posts = conn.execute('SELECT * FROM posts ORDER BY created_at DESC').fetchall()
    return render_template('dashboard.html', posts=posts)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
