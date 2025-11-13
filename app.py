import yt_dlp , time
from flask import Flask, request, jsonify
from ytmusicapi import YTMusic 
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

ytmusic = YTMusic("headers_auth.json")  

@app.route("/")
def home():
    return jsonify({"message": "YouTube Music API Flask Server Running"})

@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("q")
    
    if not query:
        return jsonify({"error": "Missing query parameter 'q'"}), 400

    results = ytmusic.search(query)
    
    res = [r for r in results if r.get("resultType") != "video"]
    return jsonify(res)



@app.route("/song/<_id>", methods=["GET"])
def song(_id):
    s = time.time()
    raw = ytmusic.get_song(_id)
    url = f"https://www.youtube.com/watch?v={_id}"

    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": False,
        "cachedir": False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    artists = info.get("artists", [])
    author = []

    def fetch_artist_data(artist_name):
        temp = ytmusic.search(artist_name, filter="artists", limit=1)
        if temp and temp[0]["resultType"] == "artist":
            artist = temp[0]
            return {
                "name": artist_name,
                "id": artist["artists"][0]["id"] if artist.get("artists") else None,
                "thumbnails": artist.get("thumbnails", []),
            }

    # parallel fetch using thread pool to reduce waiting time
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(fetch_artist_data, artists))

    author = [r for r in results if r]


    formats = info.get("formats", [])
    download_url, fmt_note = None, None
    if len(formats) > 6 and formats[6].get("format_note") == "medium":
        download_url = formats[6]["url"]
        fmt_note = formats[6]["format_note"]
    elif len(formats) > 5:
        download_url = formats[5]["url"]
        fmt_note = formats[5]["format_note"]

  
    thumbnails = raw["videoDetails"]["thumbnail"]["thumbnails"]
    data = {
        "downloadURL": download_url,
        "Format": fmt_note,
        "title": info.get("title"),
        "author": author,
        "duration": info.get("duration"),
        "duration_string": info.get("duration_string"),
        "_id": _id,
        "thumbnails": thumbnails[-1]["url"] if thumbnails else None,
    }
    taken = time.time() - s
    print(f"Processed song {_id} in {taken:.2f} seconds")
    return jsonify(info)

    

    
@app.route("/artist/<_id>", methods=["GET"])   # Done Perfect 
def artist(_id):
    info = ytmusic.get_artist(_id)
    info["songs"]["results"] = ytmusic.get_playlist(info["songs"]["browseId"])["tracks"]
    return jsonify(info)





@app.route("/playlist/<_id>", methods=["GET"])
def playlist(_id):
    info = ytmusic.get_playlist(_id)
    return jsonify(info)

if __name__ == "__main__":
    app.run(debug=True)
