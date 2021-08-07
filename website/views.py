
import pytesseract
import easyocr
import os
import json
from . import db
from flask.json import jsonify
from website.models import Post
from flask import Blueprint, request, redirect
from flask.helpers import flash
from flask.templating import render_template
from flask_login import login_required, current_user
from kraken import rpred, binarization, pageseg
from kraken.lib import models, vgsl
from PIL import Image
""" from werkzeug.utils import secure_filename """


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
        ocr_type = request.form.get('type')

        # setting img dir
        dir_path = os.path.dirname(os.path.realpath(__file__))
        img_dir = os.path.join(dir_path, 'img', file.filename)
        file.save(img_dir)

        text = ''

        # choosing ocr
        if ocr_type == 'Tesseract':
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(img_dir, config=custom_config)
        elif ocr_type == 'Kraken':
            post_image = Image.open(img_dir)
            bw_im = binarization.nlbin(post_image)
            print(bw_im)
            seg = pageseg.segment(bw_im)
            print(seg)
        elif ocr_type == 'EasyOCR':
            reader = easyocr.Reader(['en'], gpu=False)
            results = reader.readtext(img_dir)
            for result in results:
                text += result[1] + ' '
        # saving the post
        """ new_post = Post()
        new_post.img = img_dir
        new_post.type = ocr_type
        new_post.data = text
        new_post.user_id = current_user.id
        db.session.add(new_post)
        db.session.commit()
        flash('Post added', category='success') """
    return render_template("add.html", user=current_user)
