import io
from numpy import arange, array
from pandas import DataFrame, date_range, to_datetime
import matplotlib as mpl
mpl.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import base64
from datetime import datetime, timedelta
from string import Template

def timelines(x, ystart, ystop, ax=plt, color='#0b5789', linewidth=6, headwidth=timedelta(hours=5)):
    """Plot timelines at x from ystart to ystop with given color."""
    ax.vlines(x, ystart, ystop, color, lw=linewidth)
    ax.hlines(ystart, x+headwidth, x-headwidth, color, lw=linewidth)
    ax.hlines(ystop, x+headwidth, x-headwidth, color, lw=linewidth)

class DeltaTemplate(Template):
    delimiter = "%"

def strfdelta(tdelta, fmt):
    d = {"D": tdelta.days}
    d["H"], rem = divmod(tdelta.seconds, 3600)
    d["M"], d["S"] = divmod(rem, 60)
    t = DeltaTemplate(fmt)
    return t.substitute(**d)

def plot_weights(weights):
    '''
    plots weights
    '''
    plot_df = DataFrame(weights)
    # fill with missing dates
    all_date_idx = date_range(plot_df['date'].min(), plot_df['date'].max())
    plot_df['date'] = to_datetime(plot_df['date'])
    plot_df = plot_df.drop_duplicates('date')
    plot_df = plot_df.set_index('date').reindex(all_date_idx)
    plot_df['date'] = plot_df.index
    plot_df['rolling_small'] = plot_df['weight'].rolling(7, min_periods=1).mean()
    plot_df['rolling_large'] = plot_df['weight'].rolling(21, min_periods=1).mean()

    img = io.BytesIO()
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

    # mean part

    mean_ax = plt.subplot2grid((3,1),(2,0), sharex=ax)
    #
    y1 = array(plot_df['rolling_small'])
    y2 = array(plot_df['rolling_large'])
    mean_ax.fill_between(dates, y1, y2, where=y2 >= y1, facecolor='green', interpolate=True)
    mean_ax.fill_between(dates, y1, y2, where=y2 <= y1, facecolor='red', interpolate=True)
    mean_ax.grid()

    ax.xaxis.set_label('time')
    for spine in ['top', 'right']:
        for tax in [ax, mean_ax]:
            tax.spines[spine].set_visible(False)
    # plt.xticks(rotation=90)
    fig.autofmt_xdate()


    plt.savefig(img, format='png', bbox_inches='tight', transparent=True)
    img.seek(0)

    return base64.b64encode(img.getvalue()).decode()
