from flask import (
    Flask, Blueprint, flash, g, redirect, render_template, request, url_for, send_from_directory
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from flaskr.auth import login_required
from flaskr.db import get_db
import datetime
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('D:\\', 'Repositories', 'cmpu395-finstagram', 'flaskr', 'static')
print(app.config['UPLOAD_FOLDER'])
bp = Blueprint('blog', __name__)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT pID, postingDate, caption, poster, filePath'
        ' FROM Photo JOIN Person ON Photo.poster = Person.username'
        ' ORDER BY postingDate DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        
        photo = request.files['photo']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if photo.filename == '':
            flash('No selected file')
            # return redirect(request.url)
        if photo and allowed_file(photo.filename):
            print('OK')
            filename = secure_filename(photo.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(filepath)

        caption = request.form['caption']
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        username = g.user['username']
        all_followers = request.form['all_followers']
        if all_followers == 'Yes':
            all_followers = 1
        else:
            all_followers = 0
        
        error = None

        if not photo:
            error = 'Photo is required.'

        if error is not None:
            flash(error)

        else:
            db = get_db()
            # update Photos
            db.execute(
                'INSERT INTO Photo (postingDate, filePath, allFollowers, caption, poster)'
                'VALUES (?, ?, ?, ?, ?)',
                (time, filename, all_followers, caption, username)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post