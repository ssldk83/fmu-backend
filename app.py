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
    fmu_path = 'Rectifier.fmu'  # FMU file in the main folder
    result = simulate_fmu(fmu_path)
    
    fig = plot_result(result)
    plot_path = os.path.join('static', 'result_plot.html')
    fig.write_html(plot_path)

    return redirect(url_for('view_plot'))

@app.route('/plot')
def view_plot():
    return render_template('/result_plot.html')

if __name__ == '__main__':
    app.run(debug=True)
