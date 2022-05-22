from asyncio.windows_events import NULL
from flask import (
    Flask, Blueprint, flash, g, redirect, render_template, request, url_for, session
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
@login_required
def index():
    db = get_db()
    user = g.user['username']

    # 1. Photos posted by users followed by me with allFollowers == 1
    # 2. Photos shared with the friend groups I am in

    # posts = db.execute(
    #     'SELECT pID, postingDate, caption, poster, filePath'
    #     ' FROM Photo JOIN Person ON Photo.poster = Person.username'
    #     ' WHERE Photo.allFollowers = 1'
    #     ' ORDER BY postingDate DESC'
    # ).fetchall()
    
    posts = db.execute(
        'SELECT pID, postingDate, caption, poster, filePath'
        ' FROM Photo JOIN Follow on Photo.poster = Follow.followee'
        ' WHERE Photo.allFollowers = 1 AND Follow.followStatus = 1 AND Follow.follower = ?'
        ' ORDER BY postingDate DESC'
        ' UNION'
        ' SELECT pID, postingDate, caption, poster, filePath'
        ' FROM Photo JOIN SharedWith on pID JOIN BelongTo on groupName '
        ,
        (user)
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    db = get_db()
    username = g.user['username']

    user_groups = db.execute(
            "SELECT groupName"
            " FROM FriendGroup"
            " WHERE groupCreator = ?",
            (username,)
        ).fetchall()
    user_groups = [item['groupName'] for item in user_groups]

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
            # update Photos
            db.execute(
                'INSERT INTO Photo (postingDate, filePath, allFollowers, caption, poster)'
                'VALUES (?, ?, ?, ?, ?)',
                (time, filename, all_followers, caption, username)
            )
            # update SharedWith
            if all_followers == 0:
                pid = db.execute('SELECT pID FROM Photo ORDER BY pID DESC LIMIT 1').fetchall()
                pid = [item['pID'] for item in pid]
                pid = pid[-1]
                for grp in request.form.getlist('groups'):
                    db.execute(
                        'INSERT INTO SharedWith (pID, groupName, groupCreator)'
                        'VALUES (?, ?, ?)',
                        (pid, grp, username)
                    )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html', groups=user_groups)

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