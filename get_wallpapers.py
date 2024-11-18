""" učitavanje wallpapera sa Pixabay-a """

from io import BytesIO
import os
import subprocess
import requests
from PIL import Image
from config import API_KEY

SEARCH_THEME = "autumn"
URL = f"https://pixabay.com/api/?key={API_KEY}&q={SEARCH_THEME}"
DIRECTORY = "/home/giz73/.Wallpapers"


def set_xfce_wallpaper(wallpaper: str) -> None:
    """Zamjeni trenutni wallpaper za dohvaćenu sliku"""
    if not os.path.exists(wallpaper):
        return
    print(wallpaper)
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


def fetch_pics() -> None:
    """dohvati slike sa servera"""
    try:
        # Provjera postoji li direktorij, i kreacija ukoliko ne
        if not os.path.exists(DIRECTORY):
            os.makedirs(DIRECTORY)
        response = requests.get(URL, headers={"accept": "application/json"}, timeout=10)
        response.raise_for_status()  # provjeri greške HTTP zahtjeva

        data = response.json()

        for hit in data.get("hits", []):
            # provjera dimenzija slike za ekran monitora
            if hit["imageWidth"] > hit["imageHeight"]:
                image_url = hit["largeImageURL"]
                img_name = f"{hit["id"]}.jpg"
                image_path = os.path.join(DIRECTORY, img_name)

                # Preuzimanje slike ako s takvim imenom već ne postoji
                if not os.path.exists(image_path):
                    image_response = requests.get(image_url, timeout=10)
                    img = Image.open(BytesIO(image_response.content))

                    # Spremanje slike u "direktorij"
                    img.save(image_path, format="JPEG")
                    break  # zaustavi petlju nakon prve slike
        set_xfce_wallpaper(image_path)

    except requests.exceptions.Timeout:
        print("Zahtjev istekao! Pokušaj ponovo.")
    except Exception as err:
        print(f"Došlo je do greške: {err}")
        raise


def main() -> None:
    """glavna funkcija programa"""
    if not os.environ.get("DISPLAY", None):
        print("$DISPLAY not set")
        return
    fetch_pics()


if __name__ == "__main__":
    main()
