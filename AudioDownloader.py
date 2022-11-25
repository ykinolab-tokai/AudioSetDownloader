import csv
import logging
import os
import pathlib
import shutil
import subprocess
import sys
import multiprocessing
from downloader_configs import *
from typing import Union, Optional
try:
    import pytube
except ImportError as imer:
    print("use pip install pytube to install deps.")
    exit("-1")
'''
TODO:
    The pipeline for this program is as follows:
        1. Download the video from the URL by download() function, it will return the file name of the downloaded video.
        2. Convert the video to wav file by convert_to_wav() function, it will return the file name of the converted wav file.
        3. Split the wav file by splits_audio() function, it will return the file name of the split wav file.

    But in this pipline model:
    Convert function will not run until the download function is finished, 
    as well as the split function always waiting for convert function, 
    and the next tern of download will wait for the split function.
    So the program will be very slow.

    For make this program faster, asynchronism is needed.
    Next tren of download shall not wait for the split function, 
    and the split function shall not wait for the convert function.

    The new pipline will be:
        1. download the first tern of video, put the returns to a queue. start next tern of download, no wait.
        2. convert the first tern of video, put the returns to a queue, dequeue downloaded video. start next tern of convert, no wait.
        3. split the first tern of video, put the returns to a queue, dequeue converted video. start next tern of split, no wait.

    The most time-consuming part is the download function, it is important to make it asynchronism.
    Actually, this can be implemented by multi-processing, using queue to communicate between processes.
    Currently, I have no idea how to implement this. But Multiprocessing is a implemented for this, now.


'''


def convert_to_wav(filename: str, save_dir: str) -> Union[str, None]:
    """
    :param filename:
    :param save_dir: save to which folder
    :return: converted file name
    """
    basename = os.path.basename(filename)
    name, _ = os.path.splitext(basename)
    output_name = os.path.join(save_dir, f"{name}.wav")
    ret = subprocess.run([
        "ffmpeg",
        "-i", filename,
        output_name
    ]).returncode
    if ret != 0:
        return None
    return output_name


def splits_audio(filename, start_sec: int, end_sec: int, save_dir: str) -> Union[str, None]:
    """
    After downloading, split audio file.
    :param filename:
    :param from_sec:
    :param end_sec:
    :param call_back:
    :param save_dir: save to which folder
    :return: split file name.
    """
    basename = os.path.basename(filename)
    name, _ = os.path.splitext(basename)
    output_name = os.path.join(save_dir, f"{name}.wav")
    # ffmpeg -ss 60 -i input-audio.aac -t 15 -c copy output.aac
    ret = subprocess.run([
        "ffmpeg",
        "-ss", str(start_sec),
        "-i", filename,
        # "-acodec copy",
        "-t", str(end_sec - start_sec),
        output_name
    ]).returncode
    if ret != 0:
        return None
    return output_name


def download_video(url: str, youtube_id: str, save_dir: str, highest_quality=False) -> Union[str, None]:
    """
    download youtube video from url.
    :param url:
    :param highest_quality:
    :param save_dir:
    :return: the name of downloaded file.
    """
    try:
        if highest_quality:
            logging.info(f"Downloading <{url}> with highest quality.")
            download_file_name = pytube.YouTube(url).streams.filter(progressive=True) \
                .order_by('resolution') \
                .desc() \
                .first() \
                .download()
        else:
            logging.info(f"Downloading <{url}> with default quality.")
            download_file_name = pytube.YouTube(url).streams.first().download()
        _, ext_name = os.path.splitext(download_file_name)
        moved_name = f"{save_dir}/{youtube_id}{ext_name}"
        pathlib.Path(download_file_name).rename(moved_name)
        logging.info(f"File<{moved_name}> youtube id:{youtube_id}, done.\n placed at: {moved_name}")
        return moved_name
    except Exception:
        return None


def main(csv_file: str, timer:int, remove_exist: bool):
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s - pid:%(process)d",
                        handlers=[
                            logging.FileHandler(filename=f"{csv_file}_dl.log"),
                            logging.StreamHandler(stream=sys.stdout)
                        ])
    dl_video_save_dir = f"./{csv_file}.download/"
    wav_temps_dir = f"./{csv_file}.waves/"
    splits_dir = f"./{csv_file}.splits/"
    if not os.path.exists(dl_video_save_dir):
        os.makedirs(dl_video_save_dir)
    else:
        if remove_exist:
            logging.info("Video save dir already exist. Trying to cleanup.")
            shutil.rmtree(dl_video_save_dir)
            logging.info("Cleanup done.")
            os.makedirs(dl_video_save_dir)
    if not os.path.exists(wav_temps_dir):
        os.makedirs(wav_temps_dir)
    else:
        if remove_exist:
            logging.info("Waves save dir already exist. Trying to cleanup.")
            shutil.rmtree(wav_temps_dir)
            logging.info("Cleanup done.")
            os.makedirs(wav_temps_dir)
    if not os.path.exists(splits_dir):
        os.makedirs(splits_dir)
    else:
        if remove_exist:
            logging.info("Splits save dir already exist. Trying to cleanup.")
            shutil.rmtree(splits_dir)
            logging.info("Cleanup done.")
            os.makedirs(splits_dir)
    logging.info(f"Meta from file: {csv_file}")
    split_audio_positive_label = open(f"{csv_file}.split-pos.csv", "w", buffering=20)
    with open(csv_file, "r") as csv_fin:
        reader = csv.reader(csv_fin)
        i = 0
        logging.info(f"Download timer :{timer}")
        for line in reader:
            raw = {
                "YTID": line[0],
                "start_sec": int(float(line[1].replace(" ", ""))),
                "end_sec": int(float(line[2].replace(" ", ""))),
                "positive_labels": line[3:]
            }
            if os.path.exists(f"./{wav_temps_dir}/{raw['YTID']}.wav"):
                logging.info(f"./{wav_temps_dir}/{raw['YTID']}.wav exist, download continue.")
                continue
            url = f"{YTB_URL_FORMAT.format(YTID=(ytid := raw['YTID']))}"
            moved_name = download_video(url, ytid, dl_video_save_dir, DOWN_HIGHEST_QUALITY)
            wave_name = None
            split_name = None
            if moved_name is not None:
                logging.info(f"Converting file<{moved_name}> to .wav format.")
                wave_name = convert_to_wav(moved_name, wav_temps_dir)
            else:
                logging.fatal(f"url: <{url}> failed.")
            if wave_name is None:
                logging.fatal(f"Could not convert file<{wave_name}> to wav format.")
            else:
                start = raw["start_sec"]
                end = raw["end_sec"]
                logging.info(f"Splitting file<{wave_name}>, from {start} to {end}")
                split_name = splits_audio(wave_name, start, end, splits_dir, None)

            if split_name is None:
                logging.fatal(f"Can not split file<{wave_name}> to {start}s to {end}s")
            else:
                split_audio_positive_label.write(f'''{split_name}, {'{}'.format(",".join(raw["positive_labels"]))}\n''')
                split_audio_positive_label.flush()

            if 0 < timer == i:
                break
            i += 1
    split_audio_positive_label.close()


if __name__ == "__main__":
    for csv_file in CSV_FILE_NAMES:
        assert os.path.exists(csv_file), f"csv file <{csv_file}> did not exist"
    # for using Multiprocessing:
    pool = multiprocessing.Pool(len(CSV_FILE_NAMES))
    for i in range(len(CSV_FILE_NAMES)):
        pool.apply_async(main, args=(CSV_FILE_NAMES[i], TIMER, REMOVE_EXIST_DOWNLOADS))
    print("Waiting for all subprocesses done")
    pool.close()
    pool.join()
    print("All Subprocess done.")
    # Single csv file:
    # main(CSV_FILE_NAMES[0], TIMER)