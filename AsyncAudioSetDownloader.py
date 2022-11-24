import asyncio
import pytube
import subprocess
import os
import sys
import logging
import queue
import multiprocessing
import pathlib
import csv
# download video from youtube by url
# return the downloaded video path, asyn function
async def download_video(url, high_quality=False):
    try:
        if high_quality:
            ret = pytube.YouTube(url).streams.\
            filter(progressive=True, file_extension='mp4')\
            .order_by('resolution')\
            .first().download()        
        else:
            ret = pytube.YouTube(url).streams\
            .first().download()
        return ret

    except Exception as e:
        logging.error(f"download video from<{url}> falied. donwloader massage: %s" % e)
        return None

# convert video to .wav audio, return the audio path
async def convert_video_to_audio(queue: queue.Queue):
    try:
        video_path = queue.get()
        audio_path = video_path.replace(".mp4", ".wav")
        subprocess.run(["ffmpeg", "-i", video_path, audio_path])
        return audio_path
    except Exception as e:
        logging.error("convert video to audio failed. donwloader massage: %s" % e)
        return None

# split audio by start and end time, where start and end is a integer
# return the split file path
async def split_audio(queue:queue.Queue, start, end):
    try:
        audio_path = queue.get()
        audio_split_path = audio_path.replace(".wav", f"_{start}-{end}_split.wav")
        subprocess.run(["ffmpeg", "-i", audio_path, "-ss", str(start), "-to", str(end), "-c", "copy", audio_split_path])
        return audio_split_path
    except Exception as e:
        logging.error("split audio failed. donwloader massage: %s" % e)
        return None

def main(csv_file:str, timer:int, high_quality:bool, protect_cache:bool):
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(process)d -%(message)s',
        handlers=[
            logging.FileHandler(f"{csv_file}.log"),
            logging.StreamHandler(stream=sys.stdout)
        ]
    )
    if timer >= 0:
        logging.info("Timer less than 0, will not download audio.")
        return
    logging.info("Start download video and convert to audio.")

    # create a folder to place downloaded videos
    download_folder = f"{csv_file}_download"
    converted_audio_folder = f"{csv_file}_converted_audio"
    split_audio_folder = f"{csv_file}_split_audio"
    if not os.path.exists(download_folder):
        logging.info(f"Create download folder<{download_folder}>")
        os.mkdir(download_video)
    else:
        if not protect_cache:
            logging.info(f"Delete download folder<{download_folder}>")
            pathlib.Path(download_folder).rmdir()
    if not os.path.exists(converted_audio_folder):
        logging.info(f"Create converted audio folder<{converted_audio_folder}>")
        os.mkdir(converted_audio_folder)
    else:
        if not protect_cache:
            logging.info(f"Delete converted audio folder<{converted_audio_folder}>")
            pathlib.Path(converted_audio_folder).rmdir()
    if not os.path.exists(split_audio_folder):
        os.mkdir(split_audio_folder)
    else:
        if not protect_cache:
            logging.info(f"Delete split audio folder<{split_audio_folder}>")
            pathlib.Path(split_audio_folder).rmdir()
    
    videos_to_convert = queue.Queue()
    audios_to_split = queue.Queue()
    # read csv file
    with open(csv_file, "r") as f:
        # parse csv file
        csv_reader = csv.reader(f)
        for line in csv_reader:
            raw_data = {
                "YTID": line[0],
                "start": line[1],
                "end": line[2],
                "lable": line[3:]
            }

            if protect_cache and os.path.exists(f"{download_folder}/{raw_data['YTID']}.mp4"):
                logging.info(f"Video<{raw_data['YTID']}> already exists, skip download.")
                continue
            # download video
            url = f"https://www.youtube.com/watch?v={raw_data['YTID']}"
            logging.info(f"Start download video<{url}>")
            video_path = asyncio.run(download_video(url, high_quality))
            if video_path is None:
                logging.error(f"Download video<{url}> failed.")
                continue
            else:
                logging.info(f"Download video<{url}> success.")
                # move video to download folder
                logging.info(f"Move video<{video_path}> to download folder<{download_folder}>")
                os.rename(video_path, f"{download_folder}/{raw_data['YTID']}.mp4")
                videos_to_convert.put(f"{download_folder}/{raw_data['YTID']}.mp4")
            
            # convert video to audio
            audio_path = asyncio.run(convert_video_to_audio(videos_to_convert))
            
            if audio_path is None:
                logging.error(f"Convert video<{video_path}> to audio failed.")
                continue
            else:
                logging.info(f"Convert video<{video_path}> to audio success.")
                # move audio to converted audio folder
                logging.info(f"Move audio<{audio_path}> to converted audio folder<{converted_audio_folder}>")
                os.rename(audio_path, f"{converted_audio_folder}/{raw_data['YTID']}.wav")
                audios_to_split.put(f"{converted_audio_folder}/{raw_data['YTID']}.wav")

            # split audio
            audio_split_path = asyncio.run(split_audio(audios_to_split, raw_data['start'], raw_data['end']))
            if audio_split_path is None:
                logging.error(f"Split audio<{audio_path}> failed.")
                continue
            else:
                logging.info(f"Split audio<{audio_path}> success.")
                # move audio to split audio folder
                logging.info(f"Move audio<{audio_split_path}> to split audio folder<{split_audio_folder}>")
                os.rename(audio_split_path, f"{split_audio_folder}/{raw_data['YTID']}_{raw_data['start']}-{raw_data['end']}_split.wav")
        
# main entrance
if __name__ == "__main__":
    # create a multiprocessing pool
    csv_files = []
    existing_csv_file = []
    timer = 10
    high_quality = True
    # ensure all the csv_file is exist
    for file in csv_files:
        if os.path.exists(file):
            existing_csv_file.append(file)
        else:
            logging.error(f"csv file<{file}> is not exist.")

    pool = multiprocessing.Pool(len(csv_files))
    for csv_file in existing_csv_file:
        pool.apply_async(main, args=(csv_file, timer, high_quality))