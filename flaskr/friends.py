from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('friends', __name__, url_prefix='/friends')

@login_required
def get_users():
    db = get_db()
    user = g.user['username']
    all_users = db.execute('SELECT username FROM Person').fetchall()
    all_users = [person['username'] for person in all_users if person['username'] != user]
    all_users.sort(key=lambda x:x.lower())
    return all_users

@bp.route('/new_group', methods=('GET', 'POST'))
@login_required
def new_group():

    db = get_db()
    user = g.user['username']

    all_followers = db.execute(
        'SELECT follower FROM Follow WHERE followee = ? AND followStatus = 1',
        (user)
        ).fetchall()
    all_followers = [person['follower'] for person in all_followers]
    all_followers.sort(key=lambda x:x.lower())


    if request.method == 'POST':
        group_name = request.form['group_name']
        group_description = request.form['description']
        group_members = request.form.getlist('members')

        error = None
        if not group_name:
            error = 'Group Name is required.'
        elif not group_description:
            error = 'Description is required.'
        
        if error is None:
            try:
                # add group to database
                db.execute(
                    "INSERT INTO FriendGroup (groupName, groupCreator, description) VALUES (?, ?, ?)",
                    (group_name, user, group_description),
                )
                # add members into the group
                for member in group_members:
                    db.execute(
                        "INSERT INTO BelongTo (username, groupName, groupCreator) VALUES (?, ?, ?)",
                        (member, group_name, user)
                    )
                # add the user herself into the group
                db.execute(
                        "INSERT INTO BelongTo (username, groupName, groupCreator) VALUES (?, ?, ?)",
                        (user, group_name, user)
                    )
                db.commit()
            except db.IntegrityError:
                error = f"Group Name {group_name} already exists."
            else:
                return redirect(url_for("index"))

        flash(error)

    return render_template('friends/new_group.html', all_followers=all_followers)

@bp.route('/follow', methods=('GET', 'POST'))
@login_required
def follow():
    
    db = get_db()
    user = g.user['username']
    all_users = get_users()

    followings = db.execute(
        "SELECT followee"
        " FROM Follow"
        " WHERE followStatus = 1 AND follower = ?",
        (user,)
    ).fetchall()
    followings = [item['followee'] for item in followings]

    followers = db.execute(
        "SELECT follower"
        " FROM Follow"
        " WHERE followStatus = 1 AND followee = ?",
        (user,)
    ).fetchall()
    followers = [item['follower'] for item in followers]
    non_followers = [username for username in all_users if username not in followers]
    
    if request.method == 'POST':
        new_follows = request.form.getlist('new_follow')
        try:
            for new_follow in new_follows:
                db.execute(
                    "INSERT INTO Follow (follower, followee, followStatus) VALUES (?, ?, ?)",
                    (user, new_follow, 0)
                )
            db.commit()
        except db.IntegrityError:
            flash("Oops, something went wrong!")
        else:
            flash("Follow requests sent.")
            return redirect(url_for("index"))

    return render_template('friends/follow.html', followings=followings, followers=followers, non_followers=non_followers)

@bp.route('/requests', methods=('GET', 'POST'))
@login_required
def requests():
    
    db = get_db()
    user = g.user['username']

    requesters = db.execute(
        "SELECT follower"
        " FROM Follow"
        " WHERE followStatus = 0 AND followee = ?",
        (user,)
    ).fetchall()
    requesters = [item['follower'] for item in requesters]
    num_requests = len(requesters)

    if num_requests == 0:
        flash("You have no pending requests.")
        return redirect(url_for('index'))
    else:
        if request.method == 'POST':
            responses = dict(request.form)
            for follower, response in responses.items():
                if response == 'Yes':
                    try:
                        db.execute(
                            'UPDATE Follow SET followStatus = 1'
                            ' WHERE follower = ? AND followee = ?',
                            (follower, user)
                        )
                        db.commit()
                    except db.IntegrityError:
                        flash("Oops, something went wrong!")
                    else:
                        flash("Requests accepted.")
                        return redirect(url_for("index"))
                if response == 'No':
                    try:
                        db.execute(
                            'DELETE FROM Follow'
                            ' WHERE follower = ? AND followee = ? AND followStatus = 0',
                            (follower, user)
                        )
                        db.commit()
                    except db.IntegrityError:
                        flash("Oops, something went wrong!")
                    else:
                        flash("Requests rejected.")
                        return redirect(url_for('index'))
            
    return render_template('friends/requests.html', num_requests=num_requests, requesters=requesters)