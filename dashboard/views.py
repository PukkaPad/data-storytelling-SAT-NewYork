from flask import Flask, render_template, request
import pandas as pd
import sqlite3
from bokeh.plotting import *
from bokeh.embed import components
from bokeh.models import HoverTool, FactorRange, Plot, LinearAxis, Grid, Range1d
from bokeh.layouts import layout
from bokeh.plotting import figure


app = Flask(__name__)

# Load data
conn = sqlite3.connect("../api_development/SAT_NewYork_DB.db")
cur = conn.cursor()
#cur.execute("select * from AllData")
#results = cur.fetchall()
df = pd.read_sql_query("select * from AllData", conn)
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

# l = layout([
#     bollinger(),
#     slider(),
#     linked_panning(),
# ], sizing_mode='stretch_both')

# Index page
@app.route('/')
def index():
    # Determine the selected feature
    current_feature_name = request.args.get("feature_name")
    if current_feature_name == None:
        current_feature_name = "female_per"

    # Create the plot
    plot = create_figure(current_feature_name, 10)

    # Embed plot into HTML via Flask Render
    script, div = components(plot)
    return render_template("base.html", script=script, div=div,
        feature_names=feature_names,  current_feature_name=current_feature_name)


# With debug=True, Flask server will auto-reload
# when there are code changes
if __name__ == '__main__':
    app.run(port=5000, debug=True)
