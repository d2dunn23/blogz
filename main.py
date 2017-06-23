
from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'timetogetajob'


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(2000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def login_required():
    allowed_routes = ['login', 'signup', 'blog_list', 'index']

    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    creators = User.query.all()
    return render_template('index.html', creators=creators)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash('Successful Login')
            return redirect('/new_post')
        if not user or user == '':
            flash('username does not exist.', 'error')
            return render_template('login.html')
        if user.password != password or password == '':
            flash('Incorrect password', 'error')
            return render_template('login.html')

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        if len(username) < 5 or username == '':
            flash('Username is invalid')
            return render_template('signup.html')
        if verify != password:
            flash('Password does not match password on file')
            return render_template('signup.html')
        if password == '':
            flash('Enter a password')
            return render_template('signup.html')

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('User is already on file')
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            flash('Log in Successful')
            return redirect('/new_post')
    return render_template('/signup.html')

# primary route for blog
@app.route('/blog')
def blog_list():

    if request.args.get('id'):
        id = request.args.get('id')
        single_blog = Blog.query.filter_by(id=id).first()
        blog_body = single_blog.body
        blog_title = single_blog.title
        return render_template('blogzviews.html', single_blog=single_blog)

    if request.args.get('user'):
        user = request.args.get('user')
        blog_posts = Blog.query.filter_by(owner_id=user).all()
        return render_template('blogs.html', blog_posts=blog_posts)
    else:

        blog_posts = Blog.query.all()
        return render_template('blogs.html', blog_posts=blog_posts)


@app.route('/new_post', methods=['GET', 'POST'])
def new_post():

    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':

        # get user input
        new_blog_title = request.form['new_blog_title']
        new_blog_body = request.form['new_blog_body']
        new_post = Blog(new_blog_title, new_blog_body, owner)

        title_error = ''
        body_error = ''

        if new_blog_title == '':
            title_error = 'Every post needs a title.'

        if new_blog_body == '':
            body_error = 'Please enter text in the body.'

        # if there is no error
        if not title_error and not body_error:
            db.session.add(new_post)
            db.session.commit()
            id = str(new_post.id)
            return redirect('/blog?id={}'.format(id))
        else:
            return render_template('new_post.html', body_error=body_error, title_error=title_error,
                new_blog_title=new_blog_title, new_blog_body=new_blog_body)


    blogs = Blog.query.filter_by(owner=owner).first()


    return render_template('new_post.html', owner=owner)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


if __name__ == '__main__':
    app.run()