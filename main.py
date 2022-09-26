import configparser
import hashlib
import io
import json
import os
import pathlib
from zipfile import ZipFile

from dotenv import load_dotenv
from flask import Flask, render_template, send_file
from flask_cors import CORS
from flask_wtf import FlaskForm
from qbittorrent import Client
from termcolor import colored
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired

import utils

load_dotenv()
QB_PASSWORD = os.getenv("QB_PASSWORD")

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

class AddMagnet(FlaskForm):
    magnet_uri = StringField("Magnet Link:", validators=[DataRequired()])
    password = PasswordField("Password: ", validators=[DataRequired()])

PASSWORD_HASH = os.getenv("PASSWORD_HASH")

torrent_path = "/home/otto/Skrivbord/Python/flask-seedbox2/torrents"

qb = Client("http://localhost:8080/")
qb.login("admin", QB_PASSWORD)

print(colored(qb.torrents(), "green"))

@app.route("/", methods=["POST", "GET"])
def home():
    torrents = qb.torrents()

    for torrent in torrents:
        torrent["ratio"] = round(torrent["ratio"], 2)
        torrent["size"] = utils.sizeof_fmt(torrent["size"])
        if os.path.isfile(torrent["content_path"]):
            torrent["filetype"] = torrent["content_path"].split(".")[-1]
        else:
            torrent["filetype"] = "folder"
        torrent["content_path"] = torrent["content_path"].replace(os.getcwd() + "/torrents/", "")
        torrent["state"] = torrent["state"].replace("DOWN", "").replace("UP", "")

    form = AddMagnet()
    if form.validate_on_submit():
        print(colored(hashlib.sha256(str(form.password.data).encode("utf-8")).hexdigest(), "red"))
        if hashlib.sha256(str(form.password.data).encode("utf-8")).hexdigest() == PASSWORD_HASH:
            qb.download_from_link(str(form.magnet_uri.data))

    return render_template("index.html", torrents=torrents, form=form)

@app.route("/download/<path:path>")
def download(path):
    if os.path.isfile("torrents/" + path):
        return send_file(os.getcwd()+"/torrents/" + path, as_attachment=True)
    else:
        with ZipFile("output/files.zip", "w") as f:
            for file in os.listdir("torrents/" + path):
                f.add("torrents/" + path + "/" + file)

        return send_file(
            os.getcwd() + "/output/files.zip",
            as_attachment=False
        )        

@app.route("/resume/<path:path>")
def resume(path):
    if path == "all":
        qb.resume_all()
    else:
        qb.resume(path)
    return ("", 204)

@app.route("/pause/<path:path>")
def pause(path):
    if path == "all":
        qb.pause_all()
    else:
        print(path)
        qb.pause(path)
    return ("", 204)

@app.route("/delete/<path:path>")
def delete(path):
    qb.delete(path)
    return ("", 204)

@app.route("/delete_permanently/<path:path>")
def delete_permanently(path):
    qb.delete_permanently(path)
    return ("", 204)

app.run(host="0.0.0.0", debug=True)
