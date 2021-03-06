
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
import time
""" from werkzeug.utils import secure_filename """

ocrs = ['Kraken', 'EasyOCR', 'Tesseract']


def remove_image(img_dir):
    if os.path.isfile(img_dir):
        os.remove(img_dir)


views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])
@login_required
def home():
    posts = Post.query.all()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    for post in posts:
        post.img = post.img.replace(dir_path, '')
        post.img = post.img.replace('\\', '/')
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
            if os.path.isfile(post.img):
                os.remove(post.img)

    return jsonify({})


@views.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        start = time.time()
        file = request.files['file']
        ocr_type = request.form.get('type')
        title = request.form.get('title')

        # setting img dir
        dir_path = os.path.dirname(os.path.realpath(__file__))
        img_dir = os.path.join(dir_path, 'static\img',
                               str(time.time())+file.filename)
        rec_model_path = os.path.join(
            dir_path, 'en_best.mlmodel')  # model directory
        file.save(img_dir)

        text = ''

        # choosing ocr
        if ocr_type == 'Tesseract':
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(img_dir, config=custom_config)
        elif ocr_type == 'Kraken':
            post_image = Image.open(img_dir)
            bw_im = binarization.nlbin(post_image)
            seg = pageseg.segment(bw_im)

            model2 = models.load_any(rec_model_path)
            pred_it = rpred.rpred(model2, post_image, seg)
            for record in pred_it:
                text += str(record)
        elif ocr_type == 'EasyOCR':
            reader = easyocr.Reader(['en'], gpu=False)
            results = reader.readtext(img_dir)
            for result in results:
                text += result[1] + ' '

        # saving the post
        new_post = Post()
        new_post.img = img_dir
        new_post.type = ocr_type
        new_post.title = title
        new_post.data = text
        new_post.user_id = current_user.id

        end = time.time()
        elapsed_time = end-start

        new_post.elapsed_time = str(elapsed_time)
        db.session.add(new_post)
        db.session.commit()
        return render_template("single.html", user=current_user, post=new_post)
    return render_template("add.html", user=current_user, ocrs=ocrs)


@views.route('/ocr', methods=['GET', 'POST'])
def ocr():
    text = ''
    ocr_type = ''
    elapsed_time = ''
    start = 0.0

    if request.method == 'POST':
        start = time.time()
        file = request.files['file']
        ocr_type = request.form.get('type')

        # setting img dir
        dir_path = os.path.dirname(os.path.realpath(__file__))
        img_dir = os.path.join(dir_path, 'static/img',
                               str(time.time())+file.filename)
        rec_model_path = os.path.join(
            dir_path, 'en_best.mlmodel')  # model directory
        file.save(img_dir)

        text = ''

        # choosing ocr
        if ocr_type == 'Tesseract':
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(img_dir, config=custom_config)
            remove_image(img_dir)
        elif ocr_type == 'Kraken':
            post_image = Image.open(img_dir)
            bw_im = binarization.nlbin(post_image)
            seg = pageseg.segment(bw_im)

            model2 = models.load_any(rec_model_path)
            pred_it = rpred.rpred(model2, post_image, seg)
            for record in pred_it:
                text += str(record)
            remove_image(img_dir)
        elif ocr_type == 'EasyOCR':
            reader = easyocr.Reader(['en'], gpu=False)
            results = reader.readtext(img_dir)
            for result in results:
                text += result[1] + ' '
            remove_image(img_dir)
        end = time.time()
        elapsed_time = str(end-start)
        text = '["ocr": {\"text\": \"'+text+'\"}, "ocr_type": "' + \
            ocr_type+'", "elapsed_time": "'+elapsed_time+'"]'
        return text
    return render_template("ocr.html", user=current_user, text=text, ocrs=ocrs)


@views.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    if request.method == 'POST':
        post = Post.query.get(id)
        post.title = request.form.get('title')

        db.session.add(post)
        db.session.commit()
        return render_template('single.html', user=current_user, post=post)
    else:
        post = Post.query.get(id)
        return render_template('edit.html', user=current_user, post=post, ocrs=ocrs)


@views.route('/post/<id>', methods=['GET'])
def single(id):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    post = Post.query.get(id)
    post.img = post.img.replace(dir_path, '')
    post.img = post.img.replace('\\', '/')
    return render_template('single.html', user=current_user, post=post)


@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    dir_path = os.path.dirname(os.path.realpath(__file__)) + '\\'

    posts = current_user.posts
    for post in posts:
        post.img = post.img.replace(dir_path, '')
        post.img = post.img.replace('\\', '/')
    return render_template("profile.html", user=current_user, num_posts=len(current_user.posts), posts=posts)
