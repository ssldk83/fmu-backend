from flask import Flask, request, render_template, redirect, url_for
from fmpy import simulate_fmu
from fmpy.util import plot_result
import os
import uuid
import matplotlib.pyplot as plt

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        fmu = request.files['fmu']
        fmu_filename = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()) + '.fmu')
        fmu.save(fmu_filename)

        result = simulate_fmu(fmu_filename)
        fig = plot_result(result)

        plot_path = os.path.join('static', 'result_plot.html')
        fig.write_html(plot_path)  # Use this if you're using plotly

        return redirect(url_for('view_plot'))

    return render_template('index.html')

@app.route('/plot')
def view_plot():
    return render_template('/result_plot.html')

if __name__ == '__main__':
    app.run(debug=True)
