#!venv/bin/python

from app import db, models

default_username = 'seppobacho'
existing_user = models.User.query.filter_by(username=default_username).first()
if not existing_user:
    u = models.User(username=default_username, email='r@inber.to')
    db.session.add(u)
    db.session.commit()
