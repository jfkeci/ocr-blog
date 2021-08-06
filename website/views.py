
from flask.json import jsonify
from website.models import Post
from flask import Blueprint, request, redirect
from flask.helpers import flash
from flask.templating import render_template
from flask_login import login_required, current_user
""" from werkzeug.utils import secure_filename """
from . import db
import json
import os
import easyocr


views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])
@login_required
def home():
    posts = Post.query.all()
    return render_template("home.html", posts=posts, user=current_user)


@ views.route('/delete-post', methods=['POST'])
def delete_post():
    post = json.loads(request.data)
    postId = post['postId']
    post = Post.query.get(postId)
    if post:
        if post.user_id == current_user.id:
            db.session.delete(post)
            db.session.commit()

    return jsonify({})


@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template("profile.html", user=current_user, num_posts=len(current_user.posts))


@views.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        file = request.files['file']
        dir_path = os.path.dirname(os.path.realpath(__file__))
        file.save(os.path.join(dir_path, 'img', file.filename))

        new_post = Post()
        new_post.img = '/uploads/'+file.filename
        new_post.type = request.form.get('type')
        new_post.data = 'data_data_data_data'
        new_post.user_id = current_user.id
        db.session.add(new_post)
        db.session.commit()
        flash('Post added', category='success')
    return render_template("add.html", user=current_user)
