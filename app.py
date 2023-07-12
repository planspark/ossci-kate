from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a strong secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'  # Path to your SQLite database file
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@app.context_processor
def inject_current_user():
    return dict(current_user=current_user)


# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120))
    bio = db.Column(db.String(500))
    url = db.Column(db.String(200))


# Tool model
class Tool(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(500))
    url = db.Column(db.String(200))


# Article model
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(500))
    url = db.Column(db.String(200))


# Person model
class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(500))
    url = db.Column(db.String(200))


# Login manager callback to load user
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# Routes
@app.route('/')
def index():
    tools = Tool.query.all()
    articles = Article.query.all()
    persons = Person.query.all()
    return render_template('index.html', tools=tools, articles=articles, persons=persons)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if the email already exists in the database
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('register.html', error='Email already exists.')

        # Create a new user and add it to the database
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        # Log in the newly registered user
        login_user(new_user)
        return redirect(url_for('index'))

    return render_template('register.html', error=None)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid email or password.')

    return render_template('login.html', error=None)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@app.route('/tools')
def tools():
    tools = Tool.query.all()
    print(tools)  # Add this line to print the tools data
    return render_template('tools.html', tools=tools)


@app.route('/tools/add', methods=['GET', 'POST'])
@login_required
def add_tool():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        url = request.form.get('url')

        # Create a new tool and add it to the database
        new_tool = Tool(name=name, description=description, url=url)
        db.session.add(new_tool)
        db.session.commit()

        return redirect(url_for('tools'))

    return render_template('tool_form.html')


@app.route('/tools/<int:tool_id>')
def tool_detail(tool_id):
    tool = Tool.query.get_or_404(tool_id)
    return render_template('tool_detail.html', tool=tool)


@app.route('/articles')
def articles():
    articles = Article.query.all()
    return render_template('articles.html', articles=articles)


@app.route('/articles/add', methods=['GET', 'POST'])
@login_required
def add_article():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        url = request.form.get('url')

        # Create a new article and add it to the database
        new_article = Article(title=title, description=description, url=url)
        db.session.add(new_article)
        db.session.commit()

        return redirect(url_for('articles'))

    return render_template('article_form.html')


@app.route('/articles/<int:article_id>')
def article_detail(article_id):
    article = Article.query.get_or_404(article_id)
    return render_template('article_detail.html', article=article)


@app.route('/persons')
def persons():
    persons = Person.query.all()
    return render_template('persons.html', persons=persons)


@app.route('/persons/add', methods=['GET', 'POST'])
@login_required
def add_person():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        url = request.form.get('url')

        # Create a new person and add it to the database
        new_person = Person(name=name, description=description, url=url)
        db.session.add(new_person)
        db.session.commit()

        return redirect(url_for('persons'))

    return render_template('person_form.html')


@app.route('/persons/<int:person_id>')
def person_detail(person_id):
    person = Person.query.get_or_404(person_id)
    return render_template('person_detail.html', person=person)


@app.route('/users')
def users():
    users = User.query.all()
    return render_template('users.html', users=users)

def configure_logging(app):
    # Logging Configuration
    if app.config['LOG_WITH_GUNICORN']:
        gunicorn_error_logger = logging.getLogger('gunicorn.error')
        app.logger.handlers.extend(gunicorn_error_logger.handlers)
        app.logger.setLevel(logging.DEBUG)
    else:
        file_handler = RotatingFileHandler('instance/flask-user-management.log',
                                           maxBytes=16384,
                                           backupCount=20)
        file_formatter = logging.Formatter('%(asctime)s %(levelname)s %(threadName)s-%(thread)d: %(message)s [in %(filename)s:%(lineno)d]')
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

    # Remove the default logger configured by Flask
    app.logger.removeHandler(default_handler)

    app.logger.info('Starting the Flask User Management App...')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
