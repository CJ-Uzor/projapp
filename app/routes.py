from app import app, db
from flask import render_template, flash, redirect, url_for, request, current_app, send_from_directory
from app.forms import LoginForm, RegistrationForm, EditProfileForm, \
    ProjectForm, EditProjectForm, CommentForm, TodoForm, ArtifactForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User, Project, Comment, Todo, Artifact
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime
from funcs import save_file
from config import Config
import os


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/')
@app.route('/index')
@login_required
def index():
    projects = current_user.followed_projects().all()
    return render_template('index.html', title='Home', projects=projects)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    projects = user.projects.order_by(Project.created_at.desc())
    return render_template('user.html', title='Profile', user=user, projects=projects)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} not found.')
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f'You are following {username}!')
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} not found.')
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f'You are not following {username}.')
    return redirect(url_for('user', username=username))

@app.route('/explore')
@login_required
def explore():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('explore.html', title='Explore', projects=projects)

@app.route('/projects/new', methods=['GET', 'POST'])
@login_required
def new_project():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            title = form.title.data,
            body = form.body.data,
            status = form.status.data,
            sdate = form.sdate.data,
            edate = form.edate.data,
            author = current_user
        )
        db.session.add(project)
        db.session.flush()
        new_id = project.id
        db.session.commit()
        flash('Project created successfully')
        return redirect(url_for('view_project', id=new_id))
    return render_template('new_project.html', title='New project', form=form)

@app.route('/projects/<id>', methods=['GET', 'POST'])
@login_required
def view_project(id):
    form = CommentForm()
    aform = ArtifactForm()
    project = Project.query.get(id)
    tform = TodoForm(pid = project.id)
    if form.csubmit.data and form.validate():
        comment = Comment(
            body = form.body.data,
            user_id = current_user.get_id(),
            project_id = project.id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been submitted successfully')
        return redirect(url_for('view_project', id=project.id))
    if tform.tsubmit.data and tform.validate():
        todo = Todo(
            task = tform.task.data,
            edate = tform.edate.data,
            is_done = tform.is_done.data,
            project_id = project.id
        )
        db.session.add(todo)
        db.session.commit()
        flash('Task has been added successfully')
        return redirect(url_for('view_project', id=project.id))

    if aform.asubmit.data and aform.validate():
        file = request.files['file']
        fname = save_file(file)
        artifact = Artifact(
            name = aform.name.data,
            file = fname,
            project_id = project.id
        )
        db.session.add(artifact)
        db.session.commit()
        flash('Artifact saved successfully')
        return redirect(url_for('view_project', id=project.id))
    return render_template('view_project.html', title=project.title, project=project, form=form, tform=tform, aform=aform)

@app.route('/projects/<id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(id):
    project = Project.query.get(id)
    form = EditProjectForm(project.title)
    if request.method == 'GET':
        form.title.data = project.title
        form.body.data = project.body
        form.status.data = project.status
        form.sdate.data = project.sdate
        form.edate.data = project.edate
    elif form.validate_on_submit():
        project.title = form.title.data
        project.body = form.body.data
        project.status = form.status.data
        project.sdate = form.sdate.data
        project.edate = form.edate.data
        db.session.commit()
        flash('Project updated successfully!')
        return redirect(url_for('view_project', id=project.id))
    return render_template('edit_project.html', title='Edit project', form=form)

@app.route('/projects/<id>/delete', methods=['POST'])
@login_required
def delete_project(id):
    if Project.query.filter_by(id=id).delete():
        db.session.commit()
        flash('Project deleted successfully!')
        return redirect(url_for('index'))
    return redirect(url_for('view_project', id=id))

@app.route('/todos/<id>', methods=['GET', 'POST'])
@login_required
def update_todos(id):
    task = Todo.query.get(id)
    if task.is_done:
        task.is_done = False
    else:
        task.is_done = True
    db.session.commit()
    flash('Task updated successfully')
    return redirect(url_for('view_project', id=task.project.id))

@app.route('/download_file/<file>')
@login_required
def download_file(file):
    uploads = os.path.join(current_app.root_path, Config.UPLOAD_FOLDER)
    return send_from_directory(directory=uploads, filename=file)