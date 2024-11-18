""" Dohvaćanje wallpapera sa Pixabay-a """

from io import BytesIO
import os
import subprocess

import argparse
import logging
import requests
from PIL import Image
from config import API_KEY

# Postavljanje logging konfiguracije
LOG_FILE = "/home/giz73/.Wallpapers/wallpaper_downloader.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="a"),  # Spremanje u datoteku
        logging.StreamHandler(),  # Ispis u terminal
    ],
)

DIRECTORY = "/home/giz73/.Wallpapers"


def set_xfce_wallpaper(wallpaper: str) -> None:
    """Zamijeni trenutni wallpaper za dohvaćenu sliku."""
    if not os.path.exists(wallpaper):
        logging.warning(f"Wallpaper {wallpaper} ne postoji.")
        return
    proc = subprocess.run(
        ['xrandr | grep " connected"'], capture_output=True, shell=True, text=True
    )
    monitors = [line.split()[0] for line in proc.stdout.split("\n") if line]
    for monitor in monitors:
        prop_name = f"/backdrop/screen0/monitor{monitor}/workspace0/last-image"
        subprocess.run(
            [
                "xfconf-query",
                "-c",
                "xfce4-desktop",
                "-p",
                prop_name,
                "-s",
                wallpaper,
            ]
        )
    logging.info(f"Wallpaper postavljen: {wallpaper}")


def fetch_pics(theme: str) -> None:
    """Dohvati slike sa servera."""
    url = f"https://pixabay.com/api/?key={API_KEY}&q={theme}"
    try:
        if not os.path.exists(DIRECTORY):
            os.makedirs(DIRECTORY)
            logging.info(f"Direktorij kreiran: {DIRECTORY}")

        response = requests.get(url, headers={"accept": "application/json"}, timeout=10)
        response.raise_for_status()
        data = response.json()

        for hit in data.get("hits", []):
            if hit["imageWidth"] > hit["imageHeight"]:
                image_url = hit["largeImageURL"]
                img_name = f"{hit['id']}.jpg"
                image_path = os.path.join(DIRECTORY, img_name)

                if not os.path.exists(image_path):
                    logging.info(f"Dohvaćam sliku: {image_url}")
                    image_response = requests.get(image_url, timeout=10)
                    img = Image.open(BytesIO(image_response.content))
                    img.save(image_path, format="JPEG")
                    logging.info(f"Slika spremljena: {image_path}")
                    set_xfce_wallpaper(image_path)
                    return
        logging.info("Nema novih slika za preuzimanje.")

    except requests.exceptions.Timeout:
        logging.error("Zahtjev istekao! Pokušaj ponovo.")
    except Exception as err:
        logging.exception(f"Došlo je do greške: {err}")


def main() -> None:
    """Glavna funkcija programa."""
    if not os.environ.get("DISPLAY", None):
        logging.error("$DISPLAY nije postavljen. Program se ne može pokrenuti.")
        return

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--theme", default="autumn", help="Tema za pretraživanje wallpapera"
    )
    args = parser.parse_args()

    logging.info(f"Pokrećem pretraživanje wallpapera s temom: {args.theme}")
    fetch_pics(args.theme)


if __name__ == "__main__":
    main()
