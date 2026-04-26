from flask import Flask , redirect , url_for
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from Forms import EventForm, DeleteForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'your_secret_key_here'

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=True)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Event('{self.title}', '{self.date_posted}')"

@app.route('/')
@app.route('/home')
def home():
    events = Event.query.all()
    return render_template("home.html", events=events)

@app.route('/event/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    # Provide a delete form to enable CSRF-protected deletions from the detail page
    delete_form = DeleteForm()
    return render_template("event_detail.html", event=event, delete_form=delete_form)

@app.route('/create', methods=['GET', 'POST'])
def create_events():
    form = EventForm()
    if form.validate_on_submit():
        new_event = Event(
            title=form.title.data,
            description=form.description.data
            ,location=form.location.data
        )
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("create_event.html", form=form)


@app.route('/event/<int:event_id>/update', methods=['GET', 'POST'])
def update_event(event_id):
    event = Event.query.get_or_404(event_id)
    form = EventForm()
    if form.validate_on_submit():
        # Update event fields from form
        event.title = form.title.data
        event.description = form.description.data
        event.location = form.location.data
        db.session.commit()
        return redirect(url_for('event_detail', event_id=event.id))

    # Pre-populate form on GET
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
    # If CSRF failed or not submitted properly, redirect back
    return redirect(url_for('event_detail', event_id=event_id))



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='127.0.0.1', port=3000, debug=False)