from dotenv import load_dotenv
import os
from qbittorrent import Client

def qb_login():
    load_dotenv()

    QB_PASSWORD = os.getenv("QB_PASSWORD")
    torrent_path = "/home/otto/Skrivbord/Python/flask-seedbox2/torrents"

    qb = Client("http://localhost:8080/")
    qb.login("admin", QB_PASSWORD)