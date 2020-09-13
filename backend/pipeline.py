import base64
import os
import time

import imageio
import numpy as np
from skimage import img_as_ubyte
from skimage.transform import resize

import cv2
from demo import load_checkpoints, make_animation


class ModelPipeline:
    generator, kp_detector = load_checkpoints(
        config_path='config/vox-256.yaml', checkpoint_path='vox-cpk.pth.tar')

    def __init__(self, source, vid, start_time, p_id, global_status=None):
        self.source = source
        self.vid = vid
        self.start_time = start_time
        self.p_id = p_id
        self.global_status = global_status

    def update_status(self, new_status):
        if self.p_id in self.global_status and "status" in self.global_status[self.p_id]:
            p_status = self.global_status[self.p_id]
            p_status["status"] = new_status
            self.global_status[self.p_id] = p_status
        print("STATUS UPDATE: ", self.global_status, new_status, sep="\n********\n")

    def prepare(self):
        self.update_status("5")
        source, vid, start_time = self.source, self.vid, self.start_time
        os.makedirs(f"raw_images/{start_time}", exist_ok=True)
        os.makedirs(f"aligned_images/{start_time}", exist_ok=True)
        os.makedirs(f"frames/{start_time}", exist_ok=True)
        os.makedirs(f"video/intermediate/{start_time}", exist_ok=True)
        os.makedirs(f"video/final/", exist_ok=True)
        return self

    def align_images(self):
        source, vid, start_time = self.source, self.vid, self.start_time

        name = source.split("/")[-1]
        os.replace(f"{source}", f"raw_images/{start_time}/{name}")

        os.system(f"python align_images.py raw_images/{start_time}/ aligned_images/{start_time}/")
        pho_file = os.listdir(f"aligned_images/{start_time}")

        if not pho_file or not len(pho_file):
            self.update_status("Failed")
            raise ValueError("Image processing failed.")
        else:
            self.processed_image = pho_file[0]
            self.update_status("10")

        return self

    def generate_raw_output(self):
        source, vid, start_time = self.source, self.vid, self.start_time
        photoname = self.processed_image.split('.')[0] + '.png'
        source_image = imageio.imread(f'aligned_images/{start_time}/{photoname}')
        source_image = resize(source_image, (256, 256))[..., :3]

        placeholder_bytes = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip1sAAAAASUVORK5CYII=')
        placeholder_image = imageio.imread(placeholder_bytes, '.png')
        placeholder_image = resize(placeholder_image, (256, 256))[..., :3]
        ims = []
        try:
            driving_video = imageio.get_reader(vid)
            for im in driving_video:
                ims.append(im)
        except Exception as e:
            print('Error: ', e)
        
        self.update_status("20")

        driving_video = [resize(frame, (256, 256))[..., :3] for frame in driving_video]
        predictions = make_animation(source_image, driving_video, ModelPipeline.generator, ModelPipeline.kp_detector, relative=True)
        self.videoname = videoname = f'result-{start_time}.mp4'
        imageio.mimsave(f'video/intermediate/{start_time}/{videoname}', [img_as_ubyte(frame) for frame in predictions])
        self.update_status("40")
        return self

    def extract_audio_and_frames(self):
        source, vid, start_time = self.source, self.vid, self.start_time
        videoname = self.videoname

        fps_of_video = 30
        frames_of_video = int(cv2.VideoCapture(
            vid).get(cv2.CAP_PROP_FRAME_COUNT))

        vidcap = cv2.VideoCapture(f'video/intermediate/{start_time}/{videoname}')
        success, image = vidcap.read()
        count = 0
        success = True
        while success:
            cv2.imwrite(f"frames/{start_time}/frame%09d.jpg" % count, image)
            success, image = vidcap.read()
            count += 1

        frames = []
        img = os.listdir(f"frames/{start_time}/")
        img.sort()

        for i in img:
            frames.append(imageio.imread(f"frames/{start_time}/{i}"))
        frames = np.array(frames)
        self.final_video = dstvid = f"video/final/{videoname}"
        imageio.mimsave(dstvid, frames, fps=fps_of_video)
        self.update_status("60")
        return self

    def save(self):
        dstvid = self.final_video
        source, vid, start_time = self.source, self.vid, self.start_time

        tmpfile = dstvid.replace('.mp4', '-audio.mp4')
        bg_cmd = (
            f"ffmpeg -nostdin -y -i {vid} -vn -ar 44100 -ac 2 -ab 192K -f mp3 video/intermediate/{start_time}/sound.mp3"
            + " && "
            + f"ffmpeg -nostdin -i video/intermediate/{start_time}/sound.mp3 -i {dstvid} {tmpfile}"
        )
        os.system(bg_cmd)
        self.update_status("90")
        time.sleep(2)
        self.update_status("Complete")
        return self

    def pipeline(self):
        self.prepare().align_images().generate_raw_output().extract_audio_and_frames().save()
        return self
