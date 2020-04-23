from flask import Flask, render_template, send_from_directory

app = Flask(__name__, template_folder='../client/templates', static_folder='../client/static')

@app.route('/')
def home_page():
    return render_template("index.html")

@app.route('/<path:path>')
def static_response(path):
    return send_from_directory(app.static_folder, path)
