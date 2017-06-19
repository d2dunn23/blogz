
from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(2000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

# primary route for blog
@app.route('/blog')
def blog_list():

    id = request.args.get('id')
    if id:
        id = request.args.get('id')
        single_blog = Blog.query.filter_by(id=id).first()
        blog_body = single_blog.body
        blog_title = single_blog.title
        return render_template('index.html', blog_body=blog_body, blog_title=blog_title)

    blog_posts = Blog.query.all()
    return render_template('blogs.html', blog_posts=blog_posts)


@app.route('/new_post', methods=['GET', 'POST'])
def new_post():

    
    if request.method == 'POST':

        # get user input
        new_blog_title = request.form['new_blog_title']
        new_blog_body = request.form['new_blog_body']
        new_post = Blog(new_blog_title, new_blog_body)

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


    # find all entries in db
    blog_posts = db.session.query(Blog)

    return render_template('new_post.html')


if __name__ == '__main__':
app.run()