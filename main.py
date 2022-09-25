import configparser
import io
import json
import os
import pathlib
import tarfile

from dotenv import load_dotenv
from flask import Flask, render_template, send_file
from flask_cors import CORS
from qbittorrent import Client
from termcolor import colored

import utils

load_dotenv()
QB_PASSWORD = os.getenv("QB_PASSWORD")

app = Flask(__name__)
CORS(app)


torrent_path = "/home/otto/Skrivbord/Python/flask-seedbox2/torrents"

qb = Client("http://localhost:8080/")
qb.login("admin", QB_PASSWORD)

print(colored(qb.torrents(), "green"))

@app.route("/")
@app.route("/main")
@app.route("/index")
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

    return render_template("index.html", torrents=torrents)

@app.route("/download/<path:path>")
def download(path):
    if os.path.isfile("torrents/" + path):
        return send_file(os.getcwd()+"/torrents/" + path, as_attachment=True)
    else:
        with tarfile.open("output/files.tar", "w") as f:
            for file in os.listdir("torrents/" + path):
                f.add("torrents/" + path + "/" + file)

        return send_file(
            os.getcwd() + "/output/files.tar",
            as_attachment=False,
            download_filename=".tar"
        )
        

@app.route("/resume/<path:path>")
def resume(path):
    if path == "all":
        qb.resume_all()
    else:
        qb.resume(path)
    return ('', 204)

@app.route("/pause/<path:path>")
def pause(path):
    if path == "all":
        qb.pause_all()
    else:
        print(path)
        qb.pause(path)
    return ('', 204)

app.run(host="0.0.0.0", debug=True)
