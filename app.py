import yt_dlp , time
from flask import Flask, request, jsonify
from ytmusicapi import YTMusic 

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
    "format": "bestaudio/best",
    "cookiefile": "youtube.com.txt",
    "extractor_args": {
        "youtube": {
            "player_client": ["default"]  # avoids JS runtime issues
        }
    }
}
    with yt_dlp.YoutubeDL() as ydl:
        info = ydl.extract_info(url, download=False)

  
    # thumbnails = raw["videoDetails"]["thumbnail"]["thumbnails"]
    
    # data = {
    #     "downloadURL": "hh",
    #     "title": info.get("title"),
    #     "author": info["artists"],
    #     "duration": info.get("duration"),
    #     "duration_string": info.get("duration_string"),
    #     "_id": _id,
    #     "thumbnails": thumbnails[-1]["url"] if thumbnails else None,
    # }
    # taken = time.time() - s
    # print(f"Processed song {_id} in {taken:.2f} seconds")
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
