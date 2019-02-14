# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 08:49:58 2017

@author: rbomblies
"""
from flask import render_template, redirect, url_for, request, g, session, Markup
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime, timedelta

from app import app, db, lm
from pandas import DataFrame
from .forms import AddForm, LoginForm, EditForm
from .models import User, WeightEntry
from .plotting import plot_weights
#from .iplotting import iplot_worksessions

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = g.user
    weight_list = [[w.date, w.weight, w.comment] for w in user.weights.all()]
    weights = DataFrame(weight_list, columns=['date', 'weight', 'comment'])
    month_mean = weights[weights['date'] > (datetime.now() - timedelta(days=30)).date()]['weight'].mean().round(1)
    week_mean = weights[weights['date'] > (datetime.now() - timedelta(days=70)).date()]['weight'].mean().round(1)
    return render_template('index.html',
                           title='Home',
                           user=user,
                           month_mean=month_mean,
                           week_mean=week_mean)


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        if request.method == 'POST':
            username = request.form['username']
            remember_me = form.remember_me.data

            user = User.query.filter_by(username=username).first()
            login_user(user, remember = remember_me)
            return redirect(url_for('index'))

    return render_template('login.html',
                           title='Sign In',
                           form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    user = g.user
    form = AddForm()
    if request.method == 'GET':
        form.date.data = datetime.today()
    if form.validate_on_submit():
        if request.method == 'POST':
            if request.form['submit'] == "today":
                we = WeightEntry(date = datetime.now().date(),
                              weight = request.form['weight'],
                              comment = request.form['comment'],
                              user_id = user.id)
            elif request.form['submit'] == "yesterday":
                we = WeightEntry(date = datetime.now().date() - timedelta(1),
                              weight = request.form['weight'],
                              comment = request.form['comment'],
                              user_id = user.id)
            else:
                we = WeightEntry(date = datetime.strptime(request.form['date'], '%Y-%m-%d'),
                              weight = request.form['weight'],
                              comment = request.form['comment'],
                              user_id = user.id)
            db.session.add(we)
            db.session.commit()
            return redirect(url_for('index'))
    return render_template('add_data.html',
                           title='add data',
                           form=form)

@app.route('/plot')
@login_required
def plot():
    user = g.user
    weight_list = [[w.date, w.weight, w.comment] for w in user.weights.all()]
    weights = DataFrame(weight_list, columns=['date', 'weight', 'comment'])
    plot = plot_weights(weights)
    #div, script, plot = iplot_weights(weights)
    return render_template('plot.html',
                           title='Home',
                           user=user,
                           plot = plot)

@app.route('/show', methods=['GET'])
@login_required
def show():
    user = g.user
    weight_list = [[w.date, w.weight, w.comment] for w in user.weights.all()]
    weights = DataFrame(weight_list, columns=['date', 'weight', 'comment'])
    df_html = weights.set_index('date').iloc[::-1].to_html(justify='center')
    markup_df_html = Markup(df_html)
    return render_template('show_data.html',
                           title='show data',
                           df_html=markup_df_html)

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    user = g.user
    form = EditForm()
    print (form.validate_on_submit())
    print (form.weight)
    if form.validate_on_submit():
        if request.method == 'POST':
            we = user.weights.order_by('-id').first()
            we.weight = request.form['weight']
            print (we)
            db.session.commit()
            return redirect(url_for('show_data'))

    return render_template('edit_data.html',
                           title='edit data',
                           form=form
                           )
