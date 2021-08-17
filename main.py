from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
import datetime

# Delete this code:
# import requests
# posts = requests.get("https://api.npoint.io/43644ec4f0013682fc0d").json()

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


# WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField('Body', validators=[DataRequired()])
    submit = SubmitField("Submit Post")


@app.route('/')
def get_all_posts():
    posts = db.session.query(BlogPost).all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:index>")
def show_post(index):
    requested_post = db.session.query(BlogPost).get(index)
    return render_template("post.html", post=requested_post)


@app.route("/edit_post/<int:post_id>", methods=["GET", "PATCH", "POST"])
def edit_post(post_id):
    page_name = "Edit Post"
    requested_post = db.session.query(BlogPost).get(post_id)
    edit_post_form = CreatePostForm(
        title=requested_post.title,
        subtitle=requested_post.subtitle,
        author=requested_post.author,
        img_url=requested_post.img_url,
        body=requested_post.body
    )
    if edit_post_form.validate_on_submit():
        # date
        submitted_date = datetime.datetime.now()
        year = submitted_date.year
        month = submitted_date.strftime("%B")
        date = submitted_date.strftime("%d")
        # RECORDE UPDATE
        requested_post.title = edit_post_form.title.data
        requested_post.subtitle = edit_post_form.subtitle.data
        requested_post.author = edit_post_form.author.data
        requested_post.date = f"{month} {date}, {year}"
        requested_post.img_url = edit_post_form.img_url.data
        requested_post.body = edit_post_form.body.data
        # commit to db
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    return render_template("make-post.html", form=edit_post_form, page=page_name)


@app.route("/new_post", methods=["GET", "POST"])
def create_new_post():
    new_post_form = CreatePostForm()
    page_name = "New Post"
    # if entered values and press submit button
    if new_post_form.validate_on_submit():
        # date
        submitted_date = datetime.datetime.now()
        year = submitted_date.year
        month = submitted_date.strftime("%B")
        date = submitted_date.strftime("%d")
        # set data that fetch from inputs to necessary fields
        new_recorde = BlogPost(
            title=new_post_form.title.data,
            subtitle=new_post_form.subtitle.data,
            date=f"{month} {date}, {year}",
            author=new_post_form.author.data,
            img_url=new_post_form.img_url.data,
            body=new_post_form.body.data
        )
        db.session.add(new_recorde)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    return render_template("make-post.html", form=new_post_form, page=page_name)


@app.route('/delete/<int:post_id>', methods=["GET", "POST", "DELETE"])
def delete_post(post_id):
    requested_post = db.session.query(BlogPost).get(post_id)
    db.session.delete(requested_post)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True)
