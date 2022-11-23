"""
A script for mass-querying the Bar+ karaoke song index based on a CSV of wanted songs/artists.
"""

import os, csv, requests, re
from dataclasses import dataclass, asdict
from typing import Tuple, Optional, List, Dict
from time import sleep
from datetime import datetime

import click
from bs4 import BeautifulSoup


@dataclass
class BarPlusSong:
    name: str  # Title of the song
    artist: str  # Name of the song artist
    lang: str  # Language + code
    id: int  # ID in the Bar+ DB

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}


ARTIST = 0
TRACK = 1

REQUEST_DELAY = 0.2

BAR_PLUS_URL = "https://bar-plus.com/song/index"


def query_bar_plus(method: str, field: str, page=1) -> str:
    """
    Queries the Bar+ website for the particular field, and returns the resulting HTML.
    """
    field = field.lower()

    params = {
        "Song[Name]": "",
        "Song[Artist]": "",
        "Song[Language]": "",
        "Song_page": page,
        "ajax": "menu-item-grid"
    }

    if method == "artist":
        params["Song[Artist]"] = field
    if method == "track":
        params["Song[Name]"] = field

    res = requests.get(BAR_PLUS_URL, params=params)

    result = res.text

    sleep(REQUEST_DELAY)
    return result


def parse_bar_plus_html(html: str, page: int) -> Tuple[Dict[str, BarPlusSong], Optional[int]]:
    """
    Parses a page from the Bar+ song index.
    
    Returns a dict mapping artists to BarPlusSong objects, representing the songs found on the page.
    Also returns the next page number if there is an additional page, or None if there are no more pages.
    """
    soup = BeautifulSoup(html, features="html.parser")

    # get song list
    # id, title, artist, lang + mode*
    rows = soup.tbody.find_all("tr")
    songs = [[td.text for td in row.find_all("td")] for row in rows]
    if len(songs) == 1 and len(songs[0]) < 4:
        # there are no songs
        return {}, None
    songs = [BarPlusSong(song[1].strip(), song[2].strip(), song[3].strip(), song[0].strip()) for song in songs]
    artists_songs = {}
    for song in songs:
        if song.artist.lower() not in artists_songs:
            artists_songs[song.artist.lower()] = (song.artist, [song])
        else:
            artists_songs[song.artist.lower()][TRACK].append(song)

    # get last page
    li_tag = soup.find("li", attrs={"class": "last"})
    if li_tag is None:
        # only 1 page, stop here
        return artists_songs, None
    last_page_link_tag = li_tag.a
    last_page_link = last_page_link_tag["href"]
    last_page = re.search(r"Song_page=(\d+)", last_page_link).group(1)
    last_page = int(last_page)

    if page < last_page:
        return artists_songs, page + 1
    else:
        return artists_songs, None


def query_songs_by_artist(artist: str) -> List[BarPlusSong]:
    """
    Given an artist, return a list of every song by that artist in
    the Bar+ catalog.
    """
    page = 1
    all_songs = []
    while page is not None:
        html = query_bar_plus("artist", artist, page)
        songs, next_page = parse_bar_plus_html(html, page)
        if len(songs) == 0 or songs.get(artist.lower()) is None:
            # no songs
            return []
        songs = songs[artist.lower()][TRACK]  # dictionary
        all_songs.extend(songs)
        page = next_page
    return all_songs


def organize_found_songs(wanted_songs: List[str], found_songs: List[BarPlusSong]) -> Tuple[List[BarPlusSong], List[BarPlusSong], List[Tuple[str, str]]]:
    """
    Organize songs found by a certain artist.
    Return 3 lists representing:
    1. Wanted songs that were found
    2. Other songs by the same artist that were found.
    3. Wanted songs that were not found.

    Preconditions: 
    - wanted_songs and found_songs are all by the same artist
    """

    wanted_songs_dict = dict([(song.lower(), i) for i, song in enumerate(wanted_songs)])

    requested, bonus, missing = [], [], []
    for song in found_songs:
        if song.name.lower() in wanted_songs_dict:
            # Found one that we wanted!
            requested.append(song)
            # Bar+ sometimes has duplicates, but we only look at the first occurrence
            wanted_songs_dict.pop(song.name.lower())
        else:
            # Bonus!
            bonus.append(song)

    missing = [wanted_songs[i] for i in wanted_songs_dict.values()]
        
    return requested, bonus, missing


@click.command()
@click.option("--method", type=click.Choice(["csv"]), required=True, help="Method for obtaining song list.")
@click.option("--csv-path", type=click.Path(exists=True), help="Path to CSV song/artist list file")
@click.option("--strict", is_flag=True, help="Query by song name only. Faster and potentially more accurate, but will not show other songs by same artist in results.")
def main(method: str, csv_path: str, strict: bool):
    # Build dict, artist -> songs
    click.echo("Compiling artist and song lists")
    artists_songs = {}  # artist.lower() -> (artist, [songs])
    if method == "csv":
        with open(csv_path, newline='', encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=",")
            _ = next(reader)  # skip field names

            count = 0
            for row in reader:
                artist = row[ARTIST]
                name = row[TRACK]
                if artist.lower() not in artists_songs:
                    artists_songs[artist.lower()] = (artist, [name])
                else:
                    artists_songs[artist.lower()][TRACK].append(name)
                count += 1

            # for key in artists_songs:
            #     artists_songs[key].sort()
            
            click.echo(f"Lists compiled. {len(artists_songs)} total artists, {count} total songs")
    
    # Query loop, populate lists
    all_requested, all_bonus, all_missing = [], [], []
    with click.progressbar(artists_songs, length=len(artists_songs), label="Querying Bar+ song index") as bar:
        for artist_lower in bar:
            wanted_songs = artists_songs[artist_lower][TRACK]
            found_songs = query_songs_by_artist(artists_songs[artist_lower][ARTIST])
            requested, bonus, missing = organize_found_songs(wanted_songs, found_songs)
            all_requested.extend(requested)
            all_bonus.extend(bonus)
            all_missing.append((artists_songs[artist_lower][ARTIST], missing))

    # Display results (text files?)
    click.echo("Writing results to files")
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    with open(f"found-songs-{timestamp}.csv", "w", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["artist", "name", "lang", "id"], lineterminator='\n')
        writer.writerows(map(lambda x: asdict(x), sorted(all_requested, key=lambda x: x.artist)))

    if len(all_bonus) > 0 and not strict:
        with open(f"bonus-songs-{timestamp}.csv", "w", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["artist", "name", "lang", "id"], lineterminator='\n')
            writer.writerows(map(lambda x: asdict(x), sorted(all_bonus, key=lambda x: x.artist)))

    with open(f"missing-songs-{timestamp}.csv", "w", encoding="utf-8") as file:
        writer = csv.writer(file, lineterminator='\n')
        for artist, songs in all_missing:
            writer.writerows([(artist, song) for song in songs])

    click.echo("Done!")

if __name__ == "__main__":
    main()
