import os, csv, requests
from dataclasses import dataclass
from typing import Tuple, Optional, List
from time import sleep

import click
from bs4 import BeautifulSoup


@dataclass
class BarPlusSong:
    name: str  # Title of the song
    artist: str  # Name of the song artist
    lang: str  # Language
    id: int  # ID in the Bar+ DB
    code: str  # Type of song (MTV, KTV, GV, None)


ARTIST = 0
TRACK = 1

REQUEST_DELAY = 0.2

BAR_PLUS_URL = "https://bar-plus.com/song/index"

def query_bar_plus(method: str, field: str, page=1) -> str:
    """
    Queries the Bar+ website for the particular field, and returns the resulting HTML.
    """
    params = {
        "Song[Name]": "",
        "Song[Artist]": "",
        "Song[Language]": "",
        "Song_page": 1,
        "ajax": "menu-item-grid"
    }

    if method == "author":
        params["Song[Artist]"] = field
    if method == "track":
        params["Song[Name]"] = field

    res = requests.get(BAR_PLUS_URL, params=params)

    result = res.text

    sleep(REQUEST_DELAY)
    return result

def parse_bar_plus_html(html: str, page: int) -> Tuple[dict, Optional[int]]:
    """
    Parses a page from the Bar+ song index.
    
    Returns a dict mapping artists to songs, representing the songs found on the page.
    Also returns an integer if there is an additional page, or None if there are no more pages.
    """
    pass

def query_songs_by_artist(artist: str) -> List[BarPlusSong]:
    """
    Given an artist, return a list of every song by that artist in
    the Bar+ catalog.
    """
    pass


@click.command()
@click.option("--method", type=click.Choice(["csv"]), required=True)
@click.option("--csv-path", type=click.Path(exists=True))
@click.option("--query-by", type=click.Choice(["track", "author"]), required=True)
def main(method: str, csv_path: str, query_by: str):
    # Build dict, artist -> songs
    click.echo("Compiling artist and song lists...")
    artists_songs = {}
    if method == "csv":
        with open(csv_path, newline='', encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=",")
            fields = next(reader)  # skip field names
            count = 0
            for i, row in enumerate(reader):
                if row[ARTIST] not in artists_songs:
                    artists_songs[row[ARTIST]] = [row[TRACK]]
                else:
                    artists_songs[row[ARTIST]].append(row[TRACK])
                count += 1

            for key in artists_songs:
                artists_songs[key].sort()
            
            click.echo(f"Lists compiled. {len(artists_songs)} total artists, {count} total songs")
    
    # Query loop
    with click.progressbar(artists_songs, length=len(artists_songs), label="Querying Bar+ song index") as bar:
        for artist in bar:
            wanted_songs = artists_songs[artist]
            found_songs = query_songs_by_artist(artist)
            


if __name__ == "__main__":
    main()
