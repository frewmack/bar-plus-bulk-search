import os, csv

# import spotify.sync as spotify
import click

# from dotenv import load_dotenv

# load_dotenv()

# SPOTIFY_CLIENT = spotify.Client(os.getenv("SPOTIFY_CLIENT_ID"), os.getenv("SPOTIFY_CLIENT_SECRET"))

PLAYLIST_EXPORT_URL = "https://www.spotlistr.com/export/spotify-playlist"

# def authenticate():
#     pass

# def get_song_list(user: str):
#     pass

# def query_bar_plus():
#     pass

ARTIST = 0
TRACK = 1

@click.command()
@click.option("--method", type=click.Choice(["csv"]), required=True)
@click.option("--csv-path", type=click.Path(exists=True))
@click.option("--query-by", type=click.Choice(["track", "author"]), required=True)
def main(method, csv_path, query_by):
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
            
            click.echo(f"Lists compiled. {len(artists_songs)} total artists, {count} total songs")
    
    
    # Query


if __name__ == "__main__":
    main()
