from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, \
     SubmitField, TextAreaField, SelectField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from app.models import User, Project
from wtforms.fields.html5 import DateField
from wtforms_components import DateRange
from datetime import date, datetime
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed, FileRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')


class ProjectForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=4, max=140)])
    body = TextAreaField('Description', validators=[DataRequired(), Length(min=100, max=2000)])
    status = SelectField('Status',
        coerce=int,
        choices=[(0, 'Open'), (1, 'Closed'), (2, 'On hold')]
    )
    sdate = DateField(
        'Start date',
        format='%Y-%m-%d',
        validators=[DataRequired('Please select start date')]
    )
    edate = DateField(
        'End date',
        format='%Y-%m-%d',
        validators=[DataRequired('Please select end date')]
    )
    submit = SubmitField('Submit')

    def validate_edate(form, field):
        if field.data < form.sdate.data:
            raise ValidationError("End date must not be earlier than start date.")


class EditProjectForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=4, max=140)])
    body = TextAreaField('Description', validators=[DataRequired(), Length(min=100, max=300)])
    status = SelectField('Status',
        coerce=int,
        choices=[(0, 'Open'), (1, 'Closed'), (2, 'On hold')]
    )
    sdate = DateField(
        'Start date',
        format='%Y-%m-%d',
        validators=[DataRequired('Please select start date')]
    )
    edate = DateField(
        'End date',
        format='%Y-%m-%d',
        validators=[DataRequired('Please select start date')]
    )
    submit = SubmitField('Submit')

    def __init__(self, original_title, *args, **kwargs):
        super(EditProjectForm, self).__init__(*args, **kwargs)
        self.original_title = original_title

    def validate_title(self, title):
        if title.data != self.original_title:
            project = Project.query.filter_by(title=self.title.data, user_id=current_user.get_id()).first()
            if project is not None:
                raise ValidationError('Please use a different project title.')

    def validate_edate(form, field):
        if field.data < form.sdate.data:
            raise ValidationError("End date must not be earlier than start date.")


class CommentForm(FlaskForm):
    body = TextAreaField('Comment', validators=[DataRequired(), Length(min=5, max=1000)])
    csubmit = SubmitField('Submit')


class TodoForm(FlaskForm):
    pid = HiddenField()
    task = StringField('Task', validators=[DataRequired(), Length(min=4, max=140)])
    edate = DateField(
        'End date',
        format='%Y-%m-%d',
        validators=[DataRequired('Please select end date')]
    )
    is_done = BooleanField('Done', default=False)
    tsubmit = SubmitField('Submit')

    def validate_edate(form, field):
        project = Project.query.get(form.pid.data)
        if field.data < project.sdate.date() or field.data > project.edate.date():
            raise ValidationError('Make sure task end date is within the project start and end date!')


class ArtifactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=4, max=100)])
    file = FileField(
        'Add file',
        validators=[
            FileRequired(),
            FileAllowed(
                ['pdf', 'doc', 'docx'],
                'Wrong file format! Only files with extension  .pdf, .doc or .docx'
            )
        ]
    )
    asubmit = SubmitField('Submit')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')
