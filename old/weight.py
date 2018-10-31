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

def manualInput(weight_df):
    entries = ['weight', 'date', 'comments']
    # calculate last date to show in GUI
    last_date = weight_df['date'].iloc[-1]

    dlg = gtk.Dialog('Marker Label')
    dlg.show()
    # last weight
    hbox0 = gtk.HBox(True, 0)
    dlg.vbox.pack_start(hbox0)
    label = gtk.Label("last Date: ")
    label.show()
    hbox0.pack_start(label)
    label = gtk.Label(last_date)
    label.show()
    hbox0.pack_start(label)
    hbox0.show()

    entry = {}
    for data in entries:
    # weight entry hbox
        hbox = gtk.HBox(True, 0)
        dlg.vbox.pack_start(hbox)
        label = gtk.Label(data)
        label.show()
        hbox.pack_start(label)
        entry.update({data: gtk.Entry()})
        entry[data].show()
        entry[data].set_activates_default(gtk.TRUE)
        hbox.pack_start(entry[data])
        hbox.show()

    dlg.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
    dlg.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
    dlg.set_default_response(gtk.RESPONSE_OK)
    response = dlg.run()

    if response == gtk.RESPONSE_OK:
        inweight = entry['weight'].get_text()
        indate   = entry['date'].get_text()
        comments = entry['comments'].get_text()

        for key in entry:
            entry[key].set_text('')
        if indate != '':
          try:
              date = pd.to_datetime(indate, errors='raise')
          except:
              error_msg = 'Error: can\'t handle date input {}'.format(indate)
              errdlg = gtk.MessageDialog(flags=gtk.DIALOG_MODAL,
                                      buttons=gtk.BUTTONS_OK,
                                      message_format=error_msg)
              errdlg.set_title("Error.")
              errdlg.run()
              errdlg.destroy()
              return
        else:
            date = dt.date.today()

        weight = float(inweight)
        new_df = pd.DataFrame(data={'date':    date,
                                    'weight': weight,
                                    'comments': comments}, index=[0])

        return new_df
    dlg.destroy()
    return None

def parseAdd(add_string):
    try:
        weight = float(add_string)
        return dt.date.today(), weight
    except ValueError:
        return pd.to_datetime(add_string.split(',')[0]), float(add_string.split(',')[1])

################
####  main  ####
################

parser = argparse.ArgumentParser(description='Buxnbombls Personal weight monitor.')
parser.add_argument('-a', '--add', action='store_true', dest='add',
                    help='add entry. without date today is used.')
parser.add_argument('-l', '--log', type=str, dest='file',
                   default='/home/seppobacho/code/weight/weight.dat',
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
    weight_df = pd.read_csv(args.file, index_col = 0)

# connect to mysql database
con = mdb.connect('localhost', 'seppobacho', 'radlfarn', 'weightdb');

# read data from sql
#weight_df = pd.read_sql('SELECT * FROM weight_rb;', con)

# append new data from GUI
if args.add:
    print weight_df['date'].iloc[-1]
    new_weight_entry = manualInput(weight_df)
    print new_weight_entry
    weight_df = pd.concat([weight_df, new_weight_entry], axis=0)
    weight_df.reset_index(inplace=True)
    weight_df.drop('index', axis=1, inplace=True)

    #new_weight_entry.to_sql('weight_rb', con, flavor='mysql', if_exists = 'append')
    # reload the weight so new data is in there, too
    #weight_df = pd.read_sql('SELECT * FROM weight_rb;', con)
    #print weight_df.tail()

#format data
weight_df['date'] = pd.to_datetime(weight_df['date'])

# save data to csv just in case
if os.path.isfile(args.file):
    shutil.copy(args.file, '{}.bak'.format(args.file))
weight_df.to_csv(args.file, cols=['Index', 'Date', 'weight', 'comments'])
print ('weight saved to {}'.format(args.file))
con.close()

# save to Dropbox (again, just in case)
weight_df.to_csv('/home/seppobacho/Dropbox/documents/weight.dat', cols=['Index', 'Date', 'weight', 'comments'])


# plot this shit
if args.plot:
    # rolling mean
    plot_df = weight_df.copy()
    all_date_idx = pd.date_range(plot_df['date'].min(), plot_df['date'].max())
    # print pd.merge(plot_df.set_index('date'),
    #                plot_df.reindex(all_date_idx), how='outer')
    plot_df['date'] = pd.to_datetime(plot_df['date'])
    plot_df = plot_df.drop_duplicates('date')
    plot_df = plot_df.set_index('date').reindex(all_date_idx)
    plot_df['date'] = plot_df.index
    plot_df['rolling_small'] = pd.rolling_mean(plot_df['weight'], 7, min_periods=1)
    plot_df['rolling_large'] = pd.rolling_mean(plot_df['weight'], 21, min_periods=1)

    if args.plotrange != -1:
        plot_df = plot_df[len(plot_df)-args.plotrange:]

    fig = plt.figure()
    ax = plt.subplot2grid((3,1),(0,0), rowspan=2)

    # have to convert date cause scatter refuses to work with the date
    dates = [dt.date() for dt in plot_df['date']]
    ax.scatter(dates,
               plot_df['weight'],
               color = 'gray')
    ax.plot(dates, plot_df['rolling_small'], linewidth=3, color='#aa3333')
    # ax.plot(plot_df['date'], plot_df['rolling30'], linewidth=3, color='#33aa33')
    ax.grid()

    # experimental mean part

    mean_ax = plt.subplot2grid((3,1),(2,0), sharex=ax)
    #
    y1 = np.array(plot_df['rolling_small'])
    y2 = np.array(plot_df['rolling_large'])
    mean_ax.fill_between(dates, y1, y2, where=y2 >= y1, facecolor='green', interpolate=True)
    mean_ax.fill_between(dates, y1, y2, where=y2 <= y1, facecolor='red', interpolate=True)
    mean_ax.grid()

    ax.xaxis.set_label('time')
    # plt.xticks(rotation=90)
    fig.autofmt_xdate()
    plt.show()
