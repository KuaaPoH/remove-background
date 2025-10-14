from flask import Flask, render_template
from threading import Timer
import webbrowser
from werkzeug.serving import is_running_from_reloader

app = Flask(__name__)

from api import api_bp
app.register_blueprint(api_bp)

@app.route("/")
def home():
    return render_template("index.html")

def _open():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == "__main__":
    if not is_running_from_reloader():
        Timer(1, _open).start()

    app.run(debug=True)
