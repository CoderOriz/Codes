from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app
app = Flask(__name__)
app.secret_key = '1234567!@#$%^&'  # Replace with a secure secret key

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///password_manager.db'  # Use SQLite for simplicity
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
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        new_user = User(username=data['username'], password=data['password'])
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        user = User.query.filter_by(username=data['username']).first()
        if user and user.password == data['password']:
            session['username'] = user.username
            return redirect(url_for('dashboard', username=user.username))
        return jsonify({'message': 'Invalid credentials'}), 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/dashboard/<username>')
def dashboard(username):
    if 'username' not in session or session['username'] != username:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=username).first()
    if not user:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=user)

@app.route('/passwords/<username>')
def passwords(username):
    if 'username' not in session or session['username'] != username:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=username).first()
    if not user:
        return redirect(url_for('login'))
    passwords = Password.query.filter_by(user_id=user.id).all()
    return render_template('passwords.html', user=user, passwords=passwords)

@app.route('/add_password', methods=['POST'])
def add_password():
    try:
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
        return redirect(url_for('passwords', username=user.username))
    except Exception as e:
        return jsonify({'message': 'An error occurred while adding the password', 'error': str(e)}), 500

@app.route('/delete_password/<int:password_id>', methods=['POST'])
def delete_password(password_id):
    password = Password.query.get(password_id)
    if password:
        db.session.delete(password)
        db.session.commit()
    return redirect(url_for('passwords', username=request.form['username']))

if __name__ == '__main__':
    app.run(debug=True)