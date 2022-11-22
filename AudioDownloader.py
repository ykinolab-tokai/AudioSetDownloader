# import pandas as pd
import csv
import logging
import os
import pathlib
import shutil
import subprocess

from downloader_configs import *

try:
    import pytube
except ImportError as imer:
    print("use pip install pytube to install deps.")
    exit("-1")


def convert_to_wav(filename: str, save_dir: str) -> [str, None]:
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


def splits_audio(filename, start_sec: int, end_sec: int, save_dir: str, call_back) -> [str, None]:
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


def download_video(url: str, youtube_id: str, save_dir: str, highest_quality=False) -> [str, None]:
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


def main():
    dl_video_save_dir = f"./{CSV_FILE_NAME}.download/"
    wav_temps_dir = f"./{CSV_FILE_NAME}.waves/"
    splits_dir = f"./{CSV_FILE_NAME}.splits/"
    if not os.path.exists(dl_video_save_dir):
        os.makedirs(dl_video_save_dir)
    else:
        logging.info("Video save dir already exist. Trying to cleanup.")
        shutil.rmtree(dl_video_save_dir)
        logging.info("Cleanup done.")
        os.makedirs(dl_video_save_dir)
    if not os.path.exists(wav_temps_dir):
        os.makedirs(wav_temps_dir)
    else:
        logging.info("Waves save dir already exist. Trying to cleanup.")
        shutil.rmtree(wav_temps_dir)
        logging.info("Cleanup done.")
        os.makedirs(wav_temps_dir)
    if not os.path.exists(splits_dir):
        os.makedirs(splits_dir)
    else:
        logging.info("Splits save dir already exist. Trying to cleanup.")
        shutil.rmtree(splits_dir)
        logging.info("Cleanup done.")
        os.makedirs(splits_dir)
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s:%(name)s:%(message)s",
                        handlers=[
                            logging.FileHandler(f"{CSV_FILE_NAME}_dl.log"),
                            logging.StreamHandler()
                        ])
    logging.info(f"Meta from file: {CSV_FILE_NAME}")

    split_audio_positive_label = open(f"{CSV_FILE_NAME}.split-pos.csv", "w")
    with open(CSV_FILE_NAME, "r") as csv_fin:
        reader = csv.reader(csv_fin)
        i = 0
        logging.info(f"Download timer :{TIMER}")
        for line in reader:
            raw = {
                "YTID": line[0],
                "start_sec": int(float(line[1].replace(" ", ""))),
                "end_sec": int(float(line[2].replace(" ", ""))),
                "positive_labels": line[3:]
            }
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

            if 0 < TIMER == i:
                break
            i += 1
    split_audio_positive_label.close()


if __name__ == "__main__":
    main()
