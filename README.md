# AudioSetDownloader
### CAUTION:
THIS PROJECT WAS DEPRECATED, PLEASE USE [THIS PROJECT](https://github.com/LinhMuks-DFox/MuxKit.AudioSet.IO)


This is a python script specifically designed to download this 
[dataset](https://research.google.com/audioset/).

### Author information:

Name: LinhMuks-DFox

[E-mail](muxxum65536@gmail.com)

### License

This program/code in published by MIT License.

### Usage:

1. Download the Audio Set from:
    * [Evaluation](http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/eval_segments.csv)
    * [Balanced train](http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/balanced_train_segments.csv)
    * [Unbalanced train](http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/unbalanced_train_segments.csv)

2. **REMOVE** the first four lines.

    These csv files have a special format, the first 3 lines are unnecessary content. Of course, it can be kept in other places as metadata, but when running the script to try to download the audio corresponding to the script, please delete these four lines.

3. Rewrite the contents of `download_configs.py`

    This defines the constants needed during the download process.

    |          Symbols          |                            Means                             | Type   |
    | :-----------------------: | :----------------------------------------------------------: | ------ |
    |     `CSV_FILE_NAMES`      |    The paths of the csv file that needs to be downloaded     | `list` |
    |     `YTB_URL_FORMAT`      | YouTube link rules, where YTID represents the id of the video | `str`  |
    |          `TIMER`          | The maximum number of downloaded files. When timer=3, 4 files will be downloaded. | `int`  |
    |  `DOWN_HIGHEST_QUALITY`   | YouTube videos have different specifications, whether to download the highest quality specifications. | `bool` |
    | `REMOVE_EXIST_DOWNLOADS`  |          Whether to remove existing download files           | `bool` |
    |       `ONLY_AUDIO`        | **Experimental Feature** Whether to only download the audio files. | `bool` |
    | `DELETE_DOWNLOADED_VIDEO` |        Whether to remove download files after splits         | `bool` |
    |    `DELETE_WAVE_FILE`     |          Whether to remove .wav files after splits           | `bool` |

4. Run `AudioDownloader.py`

    the log will be output to the command line and the file corresponding to csv during the download process

5. For using Multi-process

    Multi-process downloading of a single file is not supported. For multiple files, a multi-process download strategy will be used. If you need to do a multi-process download of a file, consider splitting the file manually into several copies.

### Dependency

* Python version should greater than 3.4(for using `pathlib`)
* using 3rd party lib `pytube`, install it by `pip install pytube`

### For Bug

* If the downloader cannot download normally, **please consider whether the format of the csv file is legal and whether the first 3 lines have been removed.**
* YouTube videos are not stable, the links in the database may be invalid. The data that is finally successfully downloaded and its label data will be saved in the split-pos.csv file. Please use this data as a benchmark.
* In addition, the data that failed to download is also recorded in the log file by the logger, please refer to this file.
* If the experimental feature is turned on again, the program may not download properly, so please turn off the experimental feature.



#### Change Logs

* Version 1.0.0
    1. Initial Version, download, convert, split function completed,
    2. Multi-process feature added.

* Version 1.0.1

    1. Modified the format of logging
    2. Added experimental features`ONLY_AUDIO`

* Version 1.0.2
    1. New feature: New configure argument added. Weather remove downloaded video after split or not.
    2. New feature: New configure argument added. Weather remove .wav files after split or not.
    3. Type annotations of variables in config file added.
