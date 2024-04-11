from flask import *
from flask_login import *
from flask_sqlalchemy import *
import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'key' # should be in .env file in production or in docker
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
current_time = datetime.datetime.now()
formatted_time = current_time.strftime("%H:%M:%S")

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(300), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('posts', lazy=True))
    timestamp = current_time

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

# Main page
@app.route("/")
def home():
    return render_template("index.html")

# Login
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and password == user.password:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check your username and password.')

    return render_template('login.html')

 
# Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    #return render_template("dashboard.html")
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            new_post = Post(content=content, user=current_user)
            db.session.add(new_post)
            db.session.commit()

    posts = Post.query.all()
    return render_template('dashboard.html', posts=posts)


# logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


# register
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already taken. Please choose another.')
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. You can now log in.')
            return redirect(url_for('login'))

    return render_template('register.html')
    
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')
