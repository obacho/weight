from datetime import datetime, timedelta
from pandas import DataFrame
from bokeh.models import HoverTool
from bokeh.models.glyphs import Quad
from bokeh.plotting import figure
#from bokeh.plotting import Bar
from bokeh.embed import components
from bokeh.models.sources import ColumnDataSource

def create_hover_tool():
    """Generates the HTML for the Bokeh's hover data tool on our graph."""
    hover_html = """
     <div>
        <span>@x</span>
     </div>
      <div>
        <span>@hours{0.00} hours</span>
      </div>
      <div>
        <span>@check_in to @check_out</span>
      </div>
    """
    return HoverTool(tooltips=hover_html)


def create_quads(df, x, top, bottom, bar_width=.5, hover_tool=None):
    '''
        vertical quads (rectangles) at x positions from bottom to top
    '''
    tools = []
    if hover_tool:
        tools = [hover_tool,]
    source = ColumnDataSource(dict(
            left=(df[x]+timedelta(days=bar_width/2.)).values,
            top=df[top],
            right=(df[x]-timedelta(days=bar_width/2.)).values,
            bottom=df[bottom],
        )
    )


    plot = figure(plot_width=320, plot_height=200,
              x_axis_type='datetime',
              y_axis_type='datetime',
              tools=tools,
              #responsive=True,
              toolbar_location="above", )

    glyph = Quad(left="left", right="right", top="top", bottom="bottom", fill_color="#0b5789")
    plot.add_glyph(source, glyph)


    return plot

def iplot_worksessions(worksessions):
    ''' plot worksession time
        with bokeh
    '''

    # generate datapoints
    now = datetime.now()
    data = {'date': [], 'hours':[], 'check_in':[], 'check_out':[]}
    df = DataFrame()
    for sess in worksessions:
        date = datetime.combine(sess.date, datetime.min.time())
        check_in = sess.check_in.replace(year=now.year, month=now.month, day=now.day)
        if sess.check_out:
            check_out = sess.check_out.replace(year=now.year, month=now.month, day=now.day)
        else:
            check_out = now

        dp = {'date': date,
              'hours': (check_out - check_in).seconds/3600.,
              'check_in': check_in,
              'check_out': check_out}
        df = df.append(dp, ignore_index=True)

    hover = create_hover_tool()

    plot = create_quads(df,
                        x='date',
                        top='check_in',
                        bottom='check_out',
                        hover_tool=hover)
    script, div = components(plot)
    return script, div
