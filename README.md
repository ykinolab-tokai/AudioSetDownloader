# AudioSetDownloader

This is a python script specifically designed to download this [dataset](https://research.google.com/audioset/).

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

    These csv files have a special format, the first four lines are unnecessary content. Of course, it can be kept in other places as metadata, but when running the script to try to download the audio corresponding to the script, please delete these four lines.

3. Rewrite the contents of `download_configs.py`

    This defines the constants needed during the download process.

    |        Symbols         |                            Means                             |
    | :--------------------: | :----------------------------------------------------------: |
    |    `CSV_FILE_NAME`     |     The path of the csv file that needs to be downloaded     |
    |    `YTB_URL_FORMAT`    | Youtube link rules, where YTID represents the id of the video |
    |        `TIMER`         | The maximum number of downloaded files. When timer=3, 4 files will be downloaded. |
    | `DOWN_HIGHEST_QUALITY` | Youtube videos have different specifications, whether to download the highest quality specifications. |

4. Run `AudioDownloader.py`

    the log will be output to the command line and the file corresponding to csv during the download process

### Dependency

* Python version should greater than 3.4(for using `pathlib`)
* using 3rd party lib `pytube`, install it by `pip install pytube`
