from typing import List

CSV_FILE_NAMES: List[str] = ["eval_segments_1-400.csv", "eval_segments_400-.csv"]
YTB_URL_FORMAT: str = "https://www.youtube.com/watch?v={YTID}"
TIMER: int = 5  # using -1 , to download all
DOWN_HIGHEST_QUALITY: bool = True
REMOVE_EXIST_DOWNLOADS: bool = True
DEBUG: bool = False
# Experimental Features
ONLY_AUDIO: bool = False
DELETE_DOWNLOADED_VIDEO: bool = True
DELETE_WAVE_FILE: bool = True
