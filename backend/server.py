import os
import uuid

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from torch.multiprocessing import Manager, Pool, set_start_method
from utils import execute_process, prepare_files, prepare_preset_files

os.makedirs("images", exist_ok=True)
os.makedirs("videos", exist_ok=True)
os.makedirs("video/final", exist_ok=True)
os.makedirs("presets/images", exist_ok=True)
os.makedirs("presets/videos", exist_ok=True)

try:
    set_start_method('spawn')
except RuntimeError:
    pass

pool = Pool(processes=1)
app = Flask(__name__)
cors = CORS(app)

STATUS = Manager().dict()


@app.route("/upload", methods=["POST"])
def accept():
    s, d, t = prepare_files(request)
    unique_id = t

    def success(X):
        STATUS[unique_id]["status"] = "Complete"

    pool.apply_async(execute_process, [s, d, t, unique_id, STATUS], callback=success)
    STATUS[unique_id] = {
        "timestamp": t,
        "status": "Pending"
    }
    print(STATUS)
    return jsonify({"id": unique_id, "url": f"/status/{unique_id}", "timestamp": t})


@app.route("/upload-preset", methods=["POST"])
def run_preset():
    s, d, t = prepare_preset_files(request)
    unique_id = t

    def success(X):
        STATUS[unique_id]["status"] = "Complete"

    pool.apply_async(execute_process, [s, d, t, unique_id, STATUS], callback=success)
    STATUS[unique_id] = {
        "timestamp": t,
        "status": "Pending"
    }
    print(STATUS)
    return jsonify({"id": unique_id, "url": f"/status/{unique_id}", "timestamp": t})


@app.route('/status/<id>')
def taskstatus(id):
    print(STATUS)
    task = STATUS.get(id, {})
    response = None
    if "status" in task and task["status"]:
        status = task["status"]
        response = {
            'status': status
        }
        if status == "Complete":
            response["video"] = f'/videos/{task["timestamp"]}.mp4'
    else:
        response = {
            'status': "Not Found"
        }
    print(response)
    return jsonify(response)


@app.route('/')
def hello():
    return jsonify({"success": True})


@app.route('/videos', methods=["GET"])
def list_videos():
    files = [
        {"name": file_name.replace("result-", "", 1).replace("-audio", "", 1),
         "timestamp": file_name.replace("result-", "", 1).replace("-audio", "", 1).replace(".mp4", "", 1),
         "url": "/videos/{}".format(file_name.replace("result-", "", 1).replace("-audio", "", 1)),
         "ready": True
         }
        for file_name in os.listdir(app.root_path + '/video/final') if "-audio.mp4" in file_name and not file_name.startswith(".")]
    files.extend([{
        "name": f"{f['timestamp']}.mp4",
        "timestamp": f['timestamp'],
        "ready": False
    } for f in STATUS.values() if f["status"] not in ("Complete")])

    files = sorted(files, key=lambda x: x["timestamp"], reverse=True)
    return jsonify({"success": True, "videos": files})


@app.route('/videos/<filename>', methods=["GET"])
def base_static(filename):
    filename = filename.replace(".mp4", "", 1)
    print(app.root_path + '/video/final/', f"result-{filename}-audio.mp4")
    return send_from_directory(app.root_path + '/video/final/', f"result-{filename}-audio.mp4")


@app.route('/presets', methods=["GET"])
def get_presets():
    return jsonify({
        "pics": os.listdir("presets/images"),
        "videos": os.listdir("presets/videos")
    })


@app.route("/preset-assets/<filepath>/<imagepath>", methods=['GET'])
def preset_images(filepath, imagepath):
    return send_from_directory(app.root_path + f'/presets/{filepath}/', imagepath)


if __name__ == "__main__":
    app.run()
