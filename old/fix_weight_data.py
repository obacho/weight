#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import sys
import os
import shutil
import datetime as dt
import argparse
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import gtk
import MySQLdb as mdb

weight_df = pd.DataFrame()


################
####  main  ####
################

parser = argparse.ArgumentParser(description='Buxnbombls Personal weight monitor.')
parser.add_argument('-a', '--add', action='store_true', dest='add',
                    help='add entry. without date today is used.')
parser.add_argument('-l', '--log', type=str, dest='file',
                   default='./weight.fitted_corruption.dat',
                   help='logfile to load and store weights.')
parser.add_argument('-p', '--plot', action='store_true',
                   help='plot weight over time.')
parser.add_argument('-pr', '--plotrange', type=int, default=360, dest='plotrange',
                   help='plot range backwards in days. -1 for all.')
parser.add_argument('-avg', '--average', dest='average', default=21,
                   help='number of days to create running average over.')

args = parser.parse_args()

# load data
if os.path.isfile(args.file):
    df = pd.DataFrame.from_csv(args.file)

df['indate'].fillna(0, inplace=True)
df = df.reset_index()
# df['offset'] = df.index[::-1]

today = dt.datetime.today().date()

df['assigned_date'] = '0'
str = '16-12-17'
print dt.datetime.strptime(str, '%y-%m-%d').date()

for index in df.index.tolist()[::-1]:
    if df.loc[index]['indate'] != '0':
        df.ix[index,'date'] = dt.datetime.strptime(df.loc[index]['indate'], '%d-%m-%y').date()
    else:
        df.ix[index,'date'] = df.ix[index+1,'date'] + dt.timedelta(days=-1)


# older datafile
predf = pd.read_csv('weight.2015-11-29.dat',
                    names = ['date', 'weight'])
predf.dropna(inplace=True)

df = pd.concat([predf, df])
print df

df[[ 'date', 'weight', 'comments']].to_csv('weight.tmp.dat')

if args.plot:
    # rolling mean
    df['rolling_small'] = pd.rolling_mean(df['weight'], 7)
    df['rolling_large'] = pd.rolling_mean(df['weight'], 21)
    df['date'] = pd.to_datetime(df['date'])

    if args.plotrange != -1:
        df = df[len(df)-args.plotrange:]

    fig = plt.figure()
    ax = plt.subplot2grid((3,1),(0,0), rowspan=2)

    # have to convert date cause scatter refuses to work with the date
    dates = [dt.date() for dt in df['date']]
    ax.scatter(dates,
               df['weight'],
               color = 'gray')
    ax.plot(dates, df['weight'], lw=0.5)
    ax.plot(dates, df['rolling_small'], linewidth=3, color='#aa3333')
    # ax.plot(df['date'], df['rolling30'], linewidth=3, color='#33aa33')
    ax.grid()

    # experimental mean part

    mean_ax = plt.subplot2grid((3,1),(2,0), sharex=ax)
    #
    y1 = np.array(df['rolling_small'])
    y2 = np.array(df['rolling_large'])
    mean_ax.fill_between(dates, y1, y2, where=y2 >= y1, facecolor='green', interpolate=True)
    mean_ax.fill_between(dates, y1, y2, where=y2 <= y1, facecolor='red', interpolate=True)
    mean_ax.grid()

    ax.xaxis.set_label('time')
    # plt.xticks(rotation=90)
    # fig.autofmt_xdate()
    import matplotlib.dates as mdates
    ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
    plt.show()
sys.exit()












# connect to mysql database
con = mdb.connect('localhost', 'seppobacho', 'radlfarn', 'weightdb');

# read data from sql
weight_df = pd.read_sql('SELECT * FROM weight_rb;', con)

# append new data from GUI
if args.add:
    print weight_df['date'].iloc[-1]
    new_weight_entry = manualInput(weight_df)
    new_weight_entry.to_sql('weight_rb', con, flavor='mysql', if_exists = 'append')
    # reload the weight so new data is in there, too
    weight_df = pd.read_sql('SELECT * FROM weight_rb;', con)
    print weight_df.tail()


# plot this shit
if args.plot:
    # rolling mean
    weight_df['rolling_small'] = pd.rolling_mean(weight_df['weight'], 7)
    weight_df['rolling_large'] = pd.rolling_mean(weight_df['weight'], 21)
    weight_df['date'] = pd.to_datetime(weight_df['date'])

    if args.plotrange != -1:
        weight_df = weight_df[len(weight_df)-args.plotrange:]

    fig = plt.figure()
    ax = plt.subplot2grid((3,1),(0,0), rowspan=2)

    # have to convert date cause scatter refuses to work with the date
    dates = [dt.date() for dt in weight_df['date']]
    ax.scatter(dates,
               weight_df['weight'],
               color = 'gray')
    ax.plot(dates, weight_df['rolling_small'], linewidth=3, color='#aa3333')
    # ax.plot(weight_df['date'], weight_df['rolling30'], linewidth=3, color='#33aa33')
    ax.grid()

    # experimental mean part

    mean_ax = plt.subplot2grid((3,1),(2,0), sharex=ax)
    #
    y1 = np.array(weight_df['rolling_small'])
    y2 = np.array(weight_df['rolling_large'])
    mean_ax.fill_between(dates, y1, y2, where=y2 >= y1, facecolor='green', interpolate=True)
    mean_ax.fill_between(dates, y1, y2, where=y2 <= y1, facecolor='red', interpolate=True)
    mean_ax.grid()

    ax.xaxis.set_label('time')
    # plt.xticks(rotation=90)
    fig.autofmt_xdate()
    plt.show()

# save data to csv just in case
if os.path.isfile(args.file):
    shutil.copy(args.file, '{}.bak'.format(args.file))
weight_df.to_csv(args.file, cols=['weight', 'comments'])

con.close()
