# Bar+ Bulk Search

A simple CLI app for bulk-searching [Bar+ Karaoke](https://bar-plus.com/song/index) for songs by artist/title.

## How to use

You need a CSV file containing song Artists and Titles. Make sure there is a header line. eg.

```csv
Artist,Title
Toto,Africa
Weezer,Buddy Holly
```

Run `./search.exe <csv_path>` in your terminal to search songs by artist. 
Add `--strict` to search songs only by title, which is faster but will yield fewer songs.

### Spotify

Create a playlist on Spotify that you would like to search with. If you want to search your Liked Songs, 
you need to `CTRL-A` your Liked Songs and add them to a playlist.

Go to https://www.spotlistr.com/export/spotify-playlist and provide a Playlist URL.
Make sure that **Artist(s) Name** and **Track Name** are the **only** fields selected, and that
`,` is the Separator. Then, download as CSV and place it in the same directory as `search.exe`.

## Development

You need Python 3.10 or greater.

Create a virtual environment and install requirements:

```
python -m venv ./venv
pip install -r requirements.txt
```
