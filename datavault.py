from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

# Configuring SQLAlchemy for SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///password_manager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Password(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service = db.Column(db.String(150), nullable=False)
    service_username = db.Column(db.String(150), nullable=False)
    service_password = db.Column(db.String(200), nullable=False)

# Initialize the database
@app.before_request
def create_tables():
    db.create_all()

# Routes
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        hashed_password = generate_password_hash(data['password'], method='sha256')
        new_user = User(username=data['username'], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        user = User.query.filter_by(username=data['username']).first()
        if user and check_password_hash(user.password, data['password']):
            return redirect(url_for('dashboard', username=user.username))
        return jsonify({'message': 'Invalid credentials'}), 401
    return render_template('login.html')

@app.route('/dashboard/<username>')
def dashboard(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return redirect(url_for('login'))
    passwords = Password.query.filter_by(user_id=user.id).all()
    return render_template('dashboard.html', user=user, passwords=passwords)

@app.route('/add_password', methods=['POST'])
def add_password():
    data = request.form
    user = User.query.filter_by(username=data['username']).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    new_password = Password(
        user_id=user.id,
        service=data['service'],
        service_username=data['service_username'],
        service_password=data['service_password']
    )
    db.session.add(new_password)
    db.session.commit()
    return redirect(url_for('dashboard', username=user.username))

if __name__ == '__main__':
    app.run(debug=True)