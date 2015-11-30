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

wdata = pd.DataFrame()

class weightEntry(gtk.Dialog):

    print 'hello'

    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.dataframe = pd.DataFrame()
        self.window.set_title("Weight Entry")
        self.window.set_default_size(300, 100)
        self.window.connect("delete_event", self.eventDelete)
        self.window.connect("destroy", self.destroy)
        self.set_default_response(gtk.RESPONSE_OK)

        frame = gtk.Frame("Enter weight")
        self.window.add(frame)
        # vertikale Box
        vbox = gtk.VBox(True, 10)
        frame.add(vbox)
        # obere hbox
        hbox1 = gtk.HBox(True, 0)
        vbox.pack_start(hbox1)
        label = gtk.Label("weight")
        label.show()
        hbox1.pack_start(label)
        self.weight_entry = gtk.Entry()
        self.weight_entry.show()
        self.weight_entry.set_activates_default(gtk.TRUE)
        hbox1.pack_start(self.weight_entry)
        hbox1.show()
        # untere hbox
        hbox2 = gtk.HBox(True, 0)
        vbox.pack_start(hbox2)
        label = gtk.Label("date (optional)")
        label.show()
        hbox2.pack_start(label)
        self.date_entry = gtk.Entry()
        self.date_entry.show()
        hbox2.pack_start(self.date_entry)
        hbox2.show()
        # buttons
        button_hbox = gtk.HBox(True, 1)
        vbox.pack_start(button_hbox)
        button = gtk.Button("enter")
        button.connect("clicked", self.enterClicked)
        button.show()
        button_hbox.pack_start(button)
        button = gtk.Button("done")
        button.connect("clicked", self.exit)
        button.show()
        button_hbox.pack_start(button)
        button_hbox.show()
        # fertig vertikale Box
        vbox.show()
        frame.show()
        self.window.show()

        if response == gtk.RESPONSE_OK:
            self.enterClicked
            self.exit

    def enterClicked(self, data=None):
        inweight = self.weight_entry.get_text()
        indate = self.date_entry.get_text()

        self.weight_entry.set_text('')
        self.date_entry.set_text('')
        if indate != '':
            try:
                date = pd.to_datetime(indate, errors='raise')
            except:
                error_msg = 'Error: can\'t handle date input {}'.format(indate)
                dlg = gtk.MessageDialog(flags=gtk.DIALOG_MODAL,
                                        buttons=gtk.BUTTONS_OK,
                                        message_format=error_msg)
                dlg.set_title("Error.")
                dlg.run()
                dlg.destroy()
                return
        else:
            date = dt.datetime.combine(dt.date.today(),
                   dt.time.min)

        weight = float(inweight)
        new_wdata = pd.DataFrame(data={'weight':[weight]},
                                index=[date])
        self.dataframe = self.dataframe.append(new_wdata)

    def getDataFrame(self):
        return self.dataframe

    def exit(self, widget):
        gtk.main_quit()

    def eventDelete(self, widget, event, data=None):
        return False

    def destroy(self, data=None):
        gtk.main_quit()

    def main(self):
        gtk.main()

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
                   default='/home/seppobacho/weight.dat',
                   help='logfile to load and store weights.')
parser.add_argument('-p', '--plot', action='store_true',
                   help='plot weight over time.')
parser.add_argument('-m', '--mean', action='store_true',
                   help='mean weight per week.')

args = parser.parse_args()

# load data
if os.path.isfile(args.file):
    wdata = pd.DataFrame.from_csv(args.file)
else:
    sys.stdout.write('no data found in file {}.'\
                     ' starting from scratch.\n'.format(args.file))

if args.add:
    enter_window = weightEntry()
    enter_window.main()
    wdata = wdata.append(enter_window.getDataFrame())

    #date, weight = parseAdd(args.add)
    #new_wdata = pd.dataFrame(data={'weight':[weight]},
    #                        index=[date])
    #wdata = wdata.append(new_wdata)

#print wdata

# artificial data
# N = 180
# weights = np.around(np.random.normal(62,0.5,N), 1)
#
# start_date = dt.datetime.combine(dt.datetime.strptime('2015-06-12','%Y-%m-%d'), dt.time.min)
#
# datelist = pd.date_range(start_date, periods=N, freq='D').tolist()

#wdata = pd.DataFrame(data={'weight':weights},
#                    index=datelist)
#wdata.to_csv(args.file)

weekly = wdata.resample("w", how=np.mean)
weekly = weekly.rename(columns={'weight': 'weekly'})
print weekly
#weekly = weekly.rename('weight','weekly')

fig = plt.figure()
ax = fig.add_subplot(111)

wdata.plot(ax=ax)
weekly.plot(ax=ax)
#all = pd.DataFrame({'wdata': wdata, 'weekly':weekly})
#all = pd.concat({'wdata':wdata, 'weekly':weekly}, axis=1)
#print all
#all.plot()
if args.plot:
    plt.show()

# save data
#if os.path.isfile(args.file):
#    shutil.copy(args.file, '{}.bak'.format(args.file))
#wdata.to_csv(args.file)
