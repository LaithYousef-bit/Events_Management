from flask import Flask, redirect, url_for
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from Forms import EventForm, DeleteForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'
db = SQLAlchemy(app)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=True)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Event('{self.title}', '{self.date_posted}')"


def seed_sample_events():
    if Event.query.count() == 0:
        events = [
            Event(
                title='City Startup Showcase',
                description='A full-day expo where local founders demonstrate products, pitch to investors, and meet mentors.',
                location='Harborview Conference Center, Downtown',
                date_posted=datetime(2026, 5, 14, 10, 0)
            ),
            Event(
                title='Creative Coding Workshop',
                description='Hands-on session for developers and designers to build interactive web projects with Python and Flask.',
                location='Riverfront Innovation Lab',
                date_posted=datetime(2026, 6, 2, 14, 30)
            ),
            Event(
                title='Community Earth Day Cleanup',
                description='Join neighbors to refresh public parks, plant trees, and celebrate sustainability with live music.',
                location='West Lake Park',
                date_posted=datetime(2026, 4, 30, 9, 0)
            ),
        ]
        db.session.bulk_save_objects(events)
        db.session.commit()


@app.route('/')
@app.route('/home')
def home():
    events = Event.query.order_by(Event.date_posted.asc()).all()
    return render_template('home.html', events=events)


@app.route('/event/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    delete_form = DeleteForm()
    return render_template('event_detail.html', event=event, delete_form=delete_form)


@app.route('/create', methods=['GET', 'POST'])
def create_events():
    form = EventForm()
    if form.validate_on_submit():
        new_event = Event(
            title=form.title.data,
            description=form.description.data,
            location=form.location.data
        )
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('create_event.html', form=form)


@app.route('/event/<int:event_id>/update', methods=['GET', 'POST'])
def update_event(event_id):
    event = Event.query.get_or_404(event_id)
    form = EventForm()
    if form.validate_on_submit():
        event.title = form.title.data
        event.description = form.description.data
        event.location = form.location.data
        db.session.commit()
        return redirect(url_for('event_detail', event_id=event.id))

    if not form.errors:
        form.title.data = event.title
        form.description.data = event.description
        form.location.data = event.location

    return render_template('update_event.html', form=form, event=event)


@app.route('/event/<int:event_id>/delete', methods=['POST'])
def delete_event(event_id):
    form = DeleteForm()
    if form.validate_on_submit():
        event = Event.query.get_or_404(event_id)
        db.session.delete(event)
        db.session.commit()
        return redirect(url_for('home'))
    return redirect(url_for('event_detail', event_id=event_id))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_sample_events()
    app.run(host='127.0.0.1', port=3000, debug=False)
