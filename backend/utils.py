import time
import traceback
import shutil
from pipeline import ModelPipeline


def prepare_files(request):
    source = request.files['source']
    timestr = time.strftime("%Y%m%d-%H%M%S")
    ext = source.filename.split(".")[-1]
    img_path = f'images/photo-{timestr}.{ext}'
    source.save(img_path)

    video = request.files['driver']
    video_ext = video.filename.split(".")[-1]
    vid_path = f'videos/video-{timestr}.{video_ext}'
    video.save(vid_path)
    return (img_path, vid_path, timestr)


def prepare_preset_files(request):
    source = request.form['source']
    timestr = time.strftime("%Y%m%d-%H%M%S")
    ext = source.split(".")[-1]
    shutil.copyfile(f"presets/images/{source}", f"images/photo-{timestr}.{ext}")
    img_path = f'images/photo-{timestr}.{ext}'

    video = request.form['driver']
    video_ext = video.split(".")[-1]
    shutil.copyfile(f"presets/videos/{video}", f"videos/video-{timestr}.{video_ext}")
    vid_path = f'videos/video-{timestr}.{video_ext}'
    return (img_path, vid_path, timestr)


def execute_process(s, d, t, id, status):
    response = None
    try:
        process = ModelPipeline(s, d, t, id, global_status=status).pipeline()
        url_to_video, timestamp = process.final_video, process.start_time
        response = {
            "success": True,
            "video": url_to_video,
            "timestamp": timestamp
        }
    except Exception as e:
        print(traceback.format_exc())
        response = {
            "success": False,
            "error": e.message
        }

    return response
