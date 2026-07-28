from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
import pymysql
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = '12345' 
app.config['SERVER_NAME'] = '127.0.0.1:5001'
serializer = URLSafeTimedSerializer(app.secret_key)

# 📧 Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'kunjalharipriya@gmail.com' 
app.config['MAIL_PASSWORD'] = 'fftz zugl umiy tspc'    
app.config['MAIL_DEFAULT_SENDER'] = ('NotesApp', 'kunjalharipriya@gmail.com')

mail = Mail(app)


MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'Kunjal123$'  
MYSQL_DB = 'notes_db'

import os
import pymysql

def get_db_connection(db_name=None):
    return pymysql.connect(
        host=os.environ.get('MYSQL_HOST', 'localhost'),
        user=os.environ.get('MYSQL_USER', 'root'),
        password=os.environ.get('MYSQL_PASSWORD', ''),
        database=db_name or os.environ.get('MYSQL_DB', 'notes_db'),
        port=int(os.environ.get('MYSQL_PORT', 3306)),
        ssl={'ssl': True},
        cursorclass=pymysql.cursors.DictCursor
    )

def init_db():
    target_db = os.environ.get('MYSQL_DB', 'notes_db')
    
    # 1. Connect without selecting a database first to ensure the database exists
    conn = get_db_connection(db_name='defaultdb')
    with conn.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {target_db};")
    conn.commit()
    conn.close()

    # 2. Connect to target database and create tables
    conn = get_db_connection(db_name=target_db)
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(100) NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
    conn.commit()
    conn.close()

# Initialize database tables on startup
init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function



@app.route('/')
@app.route('/home')
def home():
    if 'user_id' in session:
        return redirect(url_for('view_all'))
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message_body = request.form.get('message', '').strip()

        if not name or not email or not message_body:
            flash('Please fill out all required fields.', 'warning')
            return render_template('contact.html')

        # 1. Send Notification Email to Admin (Your Gmail)
        admin_msg = Message(
            subject=f"New Contact Form Submission: {subject or 'General Inquiry'}",
            recipients=['kunjalharipriya@gmail.com'],  # 👈 Sent to you
            reply_to=email
        )
        admin_msg.body = f'''You received a new message from NotesApp Contact Form:

Name: {name}
Email: {email}
Subject: {subject}

Message:
{message_body}
'''

        # 2. Send Confirmation Email to the User
        user_msg = Message(
            subject="We received your message - NotesApp",
            recipients=[email]
        )
        user_msg.body = f'''Hello {name},

Thank you for contacting NotesApp! We have received your message and will get back to you as soon as possible.

Summary of your message:
Subject: {subject}
Message:
{message_body}

Best regards,
NotesApp Support Team
'''

        try:
            # Send both emails in real time
            mail.send(admin_msg)
            mail.send(user_msg)

            flash(f'Thank you, {name}! Your message has been sent successfully.', 'success')
            return redirect(url_for('contact'))
        except Exception as e:
            print(f"Contact Mail Error: {e}")
            flash('Failed to send your message. Please check your network or try again later.', 'danger')

    return render_template('contact.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Check if username or email already exists
                cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
                existing_user = cursor.fetchone()

                if existing_user:
                    flash('Username or email already exists!', 'warning')
                    return redirect(url_for('register'))

                # Hash password and save new user
                hashed_password = generate_password_hash(password)
                cursor.execute(
                    "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                    (username, email, hashed_password)
                )
            conn.commit()
        finally:
            conn.close()

        flash('Account created successfully! Please sign in.', 'success')
        return redirect(url_for('home'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # If the user visits /login via a GET link, redirect them to the home page
    if request.method == 'GET':
        return redirect(url_for('home'))

    # Handle form submission via POST
    username = request.form['username'].strip()
    password = request.form['password']

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, username))
            user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                flash(f'Welcome back, {user["username"]}!', 'success')
                return redirect(url_for('view_all'))
            else:
                flash('Invalid username or password.', 'danger')
    finally:
        conn.close()

    return redirect(url_for('home'))


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()

            if user:
                token = serializer.dumps(email, salt='password-reset-salt')
                
                # 🛠️ HARDCODE 127.0.0.1:5001 HERE TO GUARANTEE THE PORT MATCHES YOUR APP
                reset_url = f"http://127.0.0.1:5001{url_for('reset_password_token', token=token)}"

                msg = Message('Password Reset Request - NotesApp', recipients=[email])
                msg.body = f'''Hello {user.get('username', 'User')},

To reset your password for NotesApp, please click the link below:
{reset_url}

If you did not request a password reset, simply ignore this email.

This link will expire in 1 hour.
'''
                try:
                    mail.send(msg)
                    flash('A password reset link has been sent to your email!', 'success')
                    return redirect(url_for('home'))
                except Exception as e:
                    print(f"Error sending mail: {e}")
                    flash('Failed to send email. Please check your App Password configuration.', 'danger')
            else:
                flash('If that email exists in our system, a reset link has been sent.', 'info')
                return redirect(url_for('home'))
        finally:
            conn.close()

    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password_token(token):
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)
    except (SignatureExpired, BadTimeSignature):
        flash('The reset link is invalid or has expired.', 'danger')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return render_template('reset_password.html', token=token)

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
            conn.commit()
            flash('Password reset successfully! Please sign in.', 'success')
            return redirect(url_for('home'))
        finally:
            conn.close()

    return render_template('reset_password.html', token=token)


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# Notes CRUD Routes 

@app.route('/viewall')
@login_required
def view_all():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM notes WHERE user_id = %s ORDER BY created_at DESC", 
                (session['user_id'],)
            )
            notes = cursor.fetchall()
    finally:
        conn.close()
    
    return render_template('viewall.html', notes=notes)

@app.route('/addnote', methods=['GET', 'POST'])
@login_required
def add_note():
    if request.method == 'POST':
        title = request.form['title'].strip()
        content = request.form['content'].strip()

        if not title or not content:
            flash('Title and content are required!', 'warning')
            return render_template('addnote.html')

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO notes (title, content, user_id) VALUES (%s, %s, %s)",
                    (title, content, session['user_id'])
                )
            conn.commit()
            flash('Note added successfully!', 'success')
            return redirect(url_for('view_all'))
        finally:
            conn.close()

    return render_template('addnote.html')

@app.route('/viewnotes/<int:note_id>')
@login_required
def view_note(note_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM notes WHERE id = %s AND user_id = %s", 
                (note_id, session['user_id'])
            )
            note = cursor.fetchone()
    finally:
        conn.close()

    if not note:
        flash('Note not found or unauthorized access.', 'danger')
        return redirect(url_for('view_all'))

    return render_template('viewnote.html', note=note)

@app.route('/updatenote/<int:note_id>', methods=['GET', 'POST'])
@login_required
def update_note(note_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM notes WHERE id = %s AND user_id = %s", 
                (note_id, session['user_id'])
            )
            note = cursor.fetchone()

        if not note:
            flash('Note not found or unauthorized access.', 'danger')
            return redirect(url_for('view_all'))

        if request.method == 'POST':
            title = request.form['title'].strip()
            content = request.form['content'].strip()

            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE notes SET title = %s, content = %s WHERE id = %s AND user_id = %s",
                    (title, content, note_id, session['user_id'])
                )
            conn.commit()
            flash('Note updated successfully!', 'success')
            return redirect(url_for('view_all'))

    finally:
        conn.close()

    return render_template('updatenote.html', note=note)

@app.route('/deletenote/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM notes WHERE id = %s AND user_id = %s", 
                (note_id, session['user_id'])
            )
        conn.commit()
        flash('Note deleted successfully!', 'success')
    finally:
        conn.close()

    return redirect(url_for('view_all'))


if __name__ == '__main__':
    app.run(debug=True, port=5001) 