import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)

# --- SQLAlchemy User Model ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    birthday = db.Column(db.String(100))
    address = db.Column(db.String(200))
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(100))

# Create DB and tables
with app.app_context():
    db.create_all()

# --- Routes ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        birthday = request.form.get('birthday')
        address = request.form.get('address')
        username = request.form.get('username')
        password = request.form.get('password')
        image = request.files.get('image')

        image_filename = ""
        if image and image.filename != "":
            image_filename = secure_filename(image.filename)
            image.save(f"{app.config['UPLOAD_FOLDER']}/{image_filename}")

        if User.query.filter_by(username=username).first():
            return "<h3 style='color:red'>Username already exists.</h3>"

        new_user = User(
            name=name,
            birthday=birthday,
            address=address,
            username=username,
            password=password,
            image=image_filename
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user'] = {
                'name': user.name,
                'birthday': user.birthday,
                'address': user.address,
                'image': user.image
            }
            return redirect(url_for('profile'))
        else:
            return "<h3 style='color:red'>Invalid username or password</h3>"

    return render_template('login.html')



@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))

    user = session['user']
    
    # Calculate age
    try:
        birthday = datetime.strptime(user['birthday'], '%Y-%m-%d')
        today = datetime.today()
        age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
    except Exception:
        age = 'N/A'

    return render_template('profile.html', user=user, age=age)


if __name__ == '__main__':
    app.run(debug=True)
