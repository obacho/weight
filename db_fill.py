#!venv/bin/python

from app import db, models
import pandas as pd
from datetime import datetime

default_username = 'seppobacho'
existing_user = models.User.query.filter_by(username=default_username).first()
if not existing_user:
    u = models.User(username=default_username)
    db.session.add(u)
    db.session.commit()

wdf = pd.read_csv('old/weight.dat')[['date', 'weight', 'comments']]

for idx in wdf.index:
    row = wdf.loc[idx]
    we = models.WeightEntry(date = datetime.strptime(row['date'], '%Y-%m-%d'),
                     weight = row['weight'],
                     comment = row['comments'],
                     user_id = 1)
    db.session.add(we)
db.session.commit()
