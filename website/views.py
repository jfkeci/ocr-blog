
from flask.json import jsonify
from website.models import Post
from flask import Blueprint, request
from flask.helpers import flash
from flask.templating import render_template
from flask_login import login_required, current_user
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        data_img = request.form.get('img')
        data_type = request.form.get('type')
        data_data = request.form.get('data')
        if len(data_img):
            flash('Data is too short', category='error')
        if len(data_type):
            flash('Type is too short', category='error')
        if len(data_data):
            flash('Data is too short', category='error')
        else:
            new_post = Post()
            new_post.img = data_img
            new_post.type = data_type
            new_post.data = data_data
            new_post.user_id = current_user.id
            db.session.add(new_post)
            db.session.commit()
            flash('Post added', category='success')
    return render_template("home.html")  # , user=current_user


@views.route('/delete-post', methods=['POST'])
def delete_post():
    post = json.loads(request.data)
    postId = post['postId']
    post = Post.query.get(postId)
    if post:
        if post.user_id == current_user.id:
            db.session.delete(post)
            db.session.commit()

    return jsonify({})
