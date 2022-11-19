import os

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

@click.command()
@click.option("--method", type=click.Choice(["csv"]), prompt=True, case_sensitive=False, required=True)
@click.argument("csv_path", type=click.Path(exists=True), prompt=True)
def main(method, csv_path):
    # 1 Obtain song list
    songs = []
    artists = []
    if method == "csv":
        pass


if __name__ == "__main__":
    main()
