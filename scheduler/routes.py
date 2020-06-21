from flask import render_template, url_for, flash, redirect, request, abort
from scheduler import app, db, bcrypt
from scheduler.forms import RegistrationForm, LoginForm, EventForm
from scheduler.models import User, Event
from flask_login import login_user, current_user, logout_user, login_required

# events = [
# 	{ 
# 		'author': 'Gulchachak',
# 		'start': '15:00, June 15, 2020',
# 		'end': '16:00, June 16, 2020',
# 		'subject': 'Reading',
# 		'description': 'Hulinomika'
# 	},
# 	{ 
# 		'author': 'Arthur',
# 		'start': '15:00, June 15, 2020',
# 		'end': '17:00, June 16, 2020',
# 		'subject': 'Work',
# 		'description': 'Machine learning'
# 	}
# ]

@app.route("/")
@app.route("/home")
def home():
	events = Event.query.all()
	return render_template('home.html', events=events)

@app.route("/about")
def about():
	return render_template('about.html', title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, email=form.email.data, password=hashed_password)
		db.session.add(user)
		db.session.commit()
		flash(f'Your account has been created. You are now able to log in!', 'success')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user)
			return redirect(url_for('home'))
		else:
			flash('Login unsuccessful. Please check email and password', 'danger')
	return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('home'))

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
	return render_template('account.html', title='title')

@app.route("/event/new", methods=['GET', 'POST'])
@login_required
def new_event():
	form = EventForm()
	if form.validate_on_submit():
		event = Event(start=form.start.data, end=form.end.data, subject=form.subject.data, description=form.description.data, author=current_user)
		db.session.add(event)
		db.session.commit()
		flash('Your event has been created!', 'success')
		return redirect(url_for('home'))
	return render_template('create_event.html', title='New Event', form=form, legend='New Event')

@app.route("/event/<int:event_id>")
def event(event_id):
	event = Event.query.get_or_404(event_id)
	return render_template('event.html', subject=event.subject, event=event)

@app.route("/event/<int:event_id>/update", methods=['GET', 'POST'])
@login_required
def update_event(event_id):
	event = Event.query.get_or_404(event_id)
	if event.author != current_user:
		abort(403)
	form = EventForm()
	if form.validate_on_submit():
		event.start = form.start.data
		event.end = form.end.data
		event.subject = form.subject.data
		event.description = form.description.data
		db.session.commit()
		flash('Your event has been updated!', 'success')
		return redirect(url_for('event', event_id=event.id))
	elif request.method == 'GET':
		form.start.data = event.start
		form.end.data = event.end 
		form.subject.data = event.subject 
		form.description.data = event.description
	return render_template('create_event.html', title='Update Event', form=form, legend='Update Event')

@app.route("/event/<int:event_id>/delete", methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.author != current_user:
        abort(403)
    db.session.delete(event)
    db.session.commit()
    flash('Your event has been deleted!', 'success')
    return redirect(url_for('home'))