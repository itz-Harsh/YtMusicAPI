import yt_dlp
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
    raw = ytmusic.get_song(_id)
    
    url = f"https://www.youtube.com/watch?v={_id}"
    
    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
        info = ydl.extract_info(url, download=False)
    n = len(info["artists"])
    author = []
    for i in range(n):
        temp = ytmusic.search(info["artists"][i])[0]    
        if temp["resultType"] == "artist":
            author.append({
                "name": info["artists"][i],
                "id": temp["artists"][0]["id"],
                "thumbnails": temp["thumbnails"]
            })    
    data = {
        "downloadURL" : info["formats"][6]["url"] if info["formats"][6]["format_note"] == "medium" else info["formats"][5]["url"],
        "Format": info["formats"][6]["format_note"] if info["formats"][6]["format_note"] == "medium" else info["formats"][5]["format_note"],
        "title": info["title"],
        "author": author, 
        "duration":	info["duration"],
        "duration_string": info["duration_string"],
        "_id": _id,
        "thumbnails": raw["videoDetails"]["thumbnail"]["thumbnails"][3]["url"]
        
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
