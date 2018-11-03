import tempfile

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['txt', 'csv'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        file = request.files['inputfile']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        file_path_arg = os.path.abspath(app.config["UPLOAD_FOLDER"] + f"\{filename}")
        return render_template("results.html")
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
