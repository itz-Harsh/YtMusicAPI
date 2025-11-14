import pytubefix
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

def playable(id):
    url = f"https://www.youtube.com/watch?v={id}"
    yt = pytubefix.YouTube(url, use_po_token=True)
    stream = yt.streams.get_audio_only()
    return stream.url

@app.route("/song/<_id>", methods=["GET"])
def song(_id):

    raw = ytmusic.get_song(_id)     
    thumbnails = raw["videoDetails"]["thumbnail"]["thumbnails"]
    
    data = {
        "downloadURL": playable(_id),
        "title": raw["videoDetails"]["title"],
        "author": raw["videoDetails"]["author"],
        "duration": raw["videoDetails"]["lengthSeconds"],
        "_id": _id,
        "thumbnails": thumbnails[-1]["url"] if thumbnails else None,
    }

    return jsonify(data)
    
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
