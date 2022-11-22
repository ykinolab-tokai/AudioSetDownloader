# import pandas as pd
import csv
import logging
import shutil
from downloader_configs import *
import os
import pathlib
import subprocess

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
try:
    import pytube
except ImportError as imer:
    print("use pip install pytube to install deps.")
    exit("-1")


def convert_to_wav(filename: str) -> [str, None]:
    """
    :param filename:
    :return: converted file name
    """
    name = os.path.basename(filename)
    output_name = os.path.join(wav_temps_dir, f"{name}.wav")
    ret = subprocess.run([
        "ffmpeg",
        "-i", filename,
        output_name
    ]).returncode
    if ret != 0:
        return None
    else:
        return output_name


def splits_audio(filename, from_sec: int, end_sec: int, call_back) -> [str, None]:
    """
    After downloading, split audio file.
    :param filename:
    :param from_sec:
    :param end_sec:
    :param call_back:
    :return: split file name.
    """
    print(filename)
    return filename


def download_video(url: str, basename:str, highest_quality=False) -> [str, None]:
    """
    download youtube video from url.
    :param url:
    :param highest_quality:
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
        return download_file_name
    except Exception:
        return None



def main():
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s:%(name)s:%(message)s",
                        handlers=[
                            logging.FileHandler(f"{CSV_FILE_NAME}_dl.log"),
                            logging.StreamHandler()
                        ])
    logging.info(f"Meta from file: {CSV_FILE_NAME}")

    split_audio_positive_label = open(f"{CSV_FILE_NAME}.split-pos.csv", "w")
    with open(CSV_FILE_NAME, "r") as csv_fin:
        reader = csv.DictReader(csv_fin)
        i = 0
        logging.info(f"Download timer :{TIMER}")
        for raw in reader:
            url = f"{YTB_URL_FORMAT.format(YTID=(ytid := raw['YTID']))}"
            download_file_name = download_video(url, DOWN_HIGHEST_QUALITY)
            moved_name = None
            wave_name = None
            split_name = None
            if download_file_name is None:
                logging.fatal(f"url: <{url}> failed.")
            else:
                _, ext_name = os.path.splitext(download_file_name)
                moved_name = f"{dl_video_save_dir}/{ytid}{ext_name}"
                pathlib.Path(download_file_name).rename(moved_name)
                logging.info(f"File<{download_file_name}> , youtube id:{ytid}, done.\n placed at: {moved_name}")

            if moved_name is not None:
                logging.info(f"Converting file<{moved_name}> to .wav format.")
                wave_name = convert_to_wav(moved_name)

            if wave_name is None:
                logging.fatal(f"Could not convert file<{wave_name}> to wav format.")
            else:
                start = raw["start_seconds"]
                end = raw["end_seconds"]
                logging.info(f"Splitting file<{wave_name}>, from {start} to {end}")
                split_name = splits_audio(wave_name, start, end, None)

            if split_name is None:
                logging.fatal(f"Can not split file<{wave_name}> to {start}s to {end}s")
            else:
                split_audio_positive_label.write(f"{split_name}, {raw['positive_labels']}\n")

            if TIMER > 0 and i == TIMER:
                break
            i += 1
    split_audio_positive_label.close()


if __name__ == "__main__":
    main()
