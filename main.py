import os
from datetime import datetime
import requests
from flask import Flask, redirect, render_template, request, session

app = Flask(__name__, static_url_path="/")
app.secret_key = "bodovoj290ads9*09s"

api_host = os.environ.get('ML_API_HOST', '').rstrip("/")


@app.before_request
def auth_check():
    if "id" not in session and request.endpoint not in ("home", "login", "static"):
        return redirect("/")


@app.route("/", methods=["GET"])
def home():
    if "id" not in session:
        return render_template("index.html")
    else:
        return redirect("/gallery")


@app.route("/login", methods=["POST"])
def login():
    id, password = request.values.get("username"), request.values.get("password")
    if "admin" == id and "bestKeptSecret" == password:
        session["id"] = "admin"
        return redirect("/gallery")
    else:
        return redirect("/")


@app.route("/logout", methods=["GET"])
def logout():
    if "id" in session:
        del session["id"]
    return redirect("/")


@app.route("/upload", methods=['GET', 'POST'])
def accept_submission():
    if request.method == 'POST':
        source = request.files['source']
        driver = request.files['driver']
        try:
            res = requests.post(api_host + "/upload", files={
                'source': (source.filename, source.stream, source.content_type),
                'driver': (driver.filename, driver.stream, driver.content_type)
            })
            data = res.json() if res.content else {}
            if "url" in data:
                return redirect(f"/video/{data['timestamp']}")
        except Exception:
            return redirect("/error")
        return render_template("video.html")
    elif request.method == 'GET':
        try:
            res = requests.get(api_host + "/presets")
            data = res.json() if res.content else {}
            print(data)
            return render_template("upload.html", api_host=api_host, pics=data["pics"], videos=data["videos"])
        except Exception:
            return redirect("/error")


@app.route("/upload-preset", methods=['POST'])
def accept_preset():
    source = request.form['source']
    driver = request.form['driver']
    try:
        res = requests.post(api_host + "/upload-preset", data={
            'source': source,
            'driver': driver
        })
        data = res.json() if res.content else {}
        if "url" in data:
            return redirect(f"/video/{data['timestamp']}")
    except Exception:
        return redirect("/error")
    return render_template("video.html")


@app.route("/gallery", methods=['GET'])
def show_smg_gallery():
    files = []
    try:
        res = requests.get(api_host + "/videos")
        data = res.json() if res.content else {}
        if "videos" in data and len(data["videos"]):
            files = [{
                "label": "",
                "time": datetime.strptime(f["timestamp"], "%Y%m%d-%H%M%S").strftime("%b %d %Y"),
                "url": f"{api_host}{f['url']}" if f["ready"] else "",
            }
                for f in data["videos"]]

        print(files)
    except Exception as e:
        print(e)
    return render_template("gallery.html", files=files)


@app.route("/video/<id>", methods=['GET'])
def show_smg_video(id):
    return render_template("video.html", status_url=f"{api_host}/status/{id}", video_host=f"{api_host}")


@app.route("/tts-model", methods=['GET'])
def show_tts_mesh_model():
    return render_template("mesh.html")


@app.route("/error", methods=['GET'])
def render_error():
    return render_template("error.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
