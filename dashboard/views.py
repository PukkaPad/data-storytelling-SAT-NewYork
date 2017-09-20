from flask import Flask, render_template, request
import pandas as pd
import sqlite3
from bokeh.plotting import *
from bokeh.embed import components
from bokeh.models import HoverTool, FactorRange, Plot, LinearAxis, Grid, Range1d
from bokeh.layouts import layout, widgetbox
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import DataTable, TableColumn, NumberFormatter
from bokeh.resources import INLINE


app = Flask(__name__)

# Load data
conn = sqlite3.connect("../api_development/SAT_NewYork_DB.db")
cur = conn.cursor()
#cur.execute("select * from AllData")
#results = cur.fetchall()
df = pd.read_sql_query("select * from AllData", conn, coerce_float=True)
#print(df.head(3))
feature_names = df.columns[0:-1].values.tolist()


df_corr = pd.read_sql_query( "select * from SAT_Correlation", conn)

# Create plot
def create_figure(current_feature_name, bins):
    #xdr = FactorRange(factors=df[current_feature_name])
    #ydr = Range1d(start=0,end=max(df['SAT_score'])*1.5)
    p = figure(title = current_feature_name, width=600, height=400)
    p.y_range = Range1d(start=min(df['SAT_score']) * 0.5, end=max(df['SAT_score'])*1.1)
    p.x_range = Range1d(start=min(df[current_feature_name]) * 0.5, end=max(df[current_feature_name])*1.1)
    p.circle(df[current_feature_name], df['SAT_score'], legend='New York')
    # Set the x axis label
    p.xaxis.axis_label = current_feature_name

    # Set the y axis label
    p.yaxis.axis_label = 'Average SAT Score'
    return p

def create_data_table():
    source = ColumnDataSource(df_corr)
    columns = [TableColumn(field = "name", title = 'Names'),
           TableColumn(field = "SAT_score", title = "SAT score", formatter = NumberFormatter(format = '.00')),
            TableColumn(field = "SAT Math Avg. Score", title = "SAT Maths - Average"),
            TableColumn(field = "SAT Writing Avg. Score", title = "SAT Writing - Average"),
            TableColumn(field = "ell_percent", title = '% English Learners'),
           TableColumn(field = "white_per", title = "% White Students"),
            TableColumn(field = "asian_per", title = "% Asian Students"),
            TableColumn(field = "black_per", title = "% Black Students"),
            TableColumn(field = "hispanic_per", title = "% Hispanic Students")]
    data_table = DataTable(source=source, columns=columns, width=1010)
    output_file("./templates/SAT_corr_table.html")
    save((widgetbox(data_table)))
    #show(widgetbox(data_table))
    #return (widgetbox(data_table))


# Index page
@app.route('/')
def index():
    # Determine the selected feature
    current_feature_name = request.args.get("feature_name")
    if current_feature_name == None:
        current_feature_name = "female_per"

    # Create the plot
    plot = create_figure(current_feature_name, 10)
    plot2 = create_data_table()
    #l = layout([plot], df_corr)

    # Embed plot into HTML via Flask Render
    script, div = components(plot)

    #script2, div2 = components(plot2)
    return render_template("base.html", script=script, div=div,
        feature_names=feature_names,  current_feature_name=current_feature_name)


# With debug=True, Flask server will auto-reload
# when there are code changes
if __name__ == '__main__':
    app.run(port=5000, debug=True)


