import json

from flask import Flask, render_template, send_file
from flask_cors import CORS
from qbittorrent import Client
from termcolor import colored
from dotenv import load_dotenv
import os
import configparser

import utils

load_dotenv()
QB_PASSWORD = os.getenv("QB_PASSWORD")

app = Flask(__name__)
CORS()


torrent_path = "/home/otto/Skrivbord/Python/flask-seedbox2/torrents"

qb = Client("http://localhost:8080/")
qb.login("admin", QB_PASSWORD)

print(colored(qb.torrents(), "green"))

#qb.download_from_link(magnet, savepath=torrent_path)

@app.route("/")
@app.route("/main")
@app.route("/index")
def home():
    return render_template("index.html", torrents=qb.torrents())

@app.route("/download/<path:path>")
def download(path):
    full_path = "torrents/"
    return send_file(os.getcwd()+"/torrents/" + path, as_attachment=True)

@app.route("/resume")
def resume():
    qb.resume_all()
    return ('', 204)

@app.route("/pause")
def pause():
    qb.pause_all()
    return ('', 204)

app.run(debug=True)
