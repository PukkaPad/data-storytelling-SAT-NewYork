#Your imports
from flask import Flask, render_template
from bokeh.embed import components
from bokeh.plotting import figure
import pandas as pd
import sqlite3
from bokeh.layouts import layout, widgetbox
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import DataTable, TableColumn
from bokeh.resources import INLINE

app = Flask(__name__)

conn = sqlite3.connect("../api_development/SAT_NewYork_DB.db")
cur = conn.cursor()
df_corr = pd.read_sql_query( "select * from SAT_Correlation", conn)

source = ColumnDataSource(df_corr)
columns = [TableColumn(field = "name", title = 'Names'),
          TableColumn(field = "SAT_score", title = "SAT score"),
          TableColumn(field = "SAT Math Avg. Score", title = "SAT Maths - Average"),
           TableColumn(field = "SAT Writing Avg. Score", title = "SAT Writing - Average"),
           TableColumn(field = "ell_percent", title = '% English Learners'),
           TableColumn(field = "white_per", title = "% White Students"),
           TableColumn(field = "asian_per", title = "% Asian Students"),
           TableColumn(field = "black_per", title = "% Black Students"),
           TableColumn(field = "hispanic_per", title = "% Hispanic Students")]
data_table = DataTable(source=source, columns=columns, width=1010)
    #show(widgetbox(data_table))
    #return (widgetbox(data_table))



@app.route('/')
def homepage():
    title = 'home'
    from bokeh.plotting import figure

    #First Plot
    p = figure(plot_width=400, plot_height=400, responsive = True)
    p.circle([1, 2, 3, 4, 5], [6, 7, 2, 4, 5], size=20, color="navy", alpha=0.5)

    #Second Plot
    plot2 = (widgetbox(data_table))


    script, div = components(p)
    script2, div2 = components(plot2)

    return render_template('index.html', title = title, script = script,
    div = div, script2 = script2, div2 = div2)

if __name__ == '__main__':
    app.run(port=5000, debug=True)



