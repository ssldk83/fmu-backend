from flask import Flask, render_template, redirect, url_for
from fmpy import simulate_fmu
from fmpy.util import plot_result
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simulate')
def simulate():
    result = simulate_fmu('Rectifier.fmu')
    fig = plot_result(result)
    fig.write_html('templates/result_plot.html')  # ✅ save where Flask can read it
    return redirect(url_for('view_plot'))

@app.route('/plot')
def view_plot():
    return render_template('result_plot.html')  # ✅ reads from templates/

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
