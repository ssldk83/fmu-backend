from flask import Flask
from custominput_app import custominput_bp

app = Flask(__name__)
app.register_blueprint(custominput_bp, url_prefix='/custominput')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
