import pathlib

import requests

from config import REQUEST_HEADERS_FOR_ALGOEXPERT_SITE, DATA_STRUCTURES_CRASH_COURSE_ENDPOINT, PARENT_DIR, \
    DATA_STRUCTURES_CRASH_COURSE_DATA_FILE_NAME, INDENTATION_SPACES, \
    DATA_STRUCTURES_CRASH_COURSE_FOLDER
from file_helper import write_python_object_to_file
from question_solution.question_solution_video_downloader import get_video_urls, download_video


def get_ds_course_data(url=DATA_STRUCTURES_CRASH_COURSE_ENDPOINT):
    response = requests.post(url, headers=REQUEST_HEADERS_FOR_ALGOEXPERT_SITE)
    return response.json()


def main():
    video_quality = '540p'
    ds_course_data_folder_path = create_data_structures_course_data_folder()
    ds_course_data = write_data_structures_course_data_file(ds_course_data_folder_path)
    for idx, ds in enumerate(ds_course_data['datastructures'], 1):
        serial_number = f"{idx}".rjust(2, '0')
        videos = get_video_urls(ds['video']['vimeoId'], video_quality)
        ds_file_path = ds_course_data_folder_path / f"{serial_number} {ds['name']}_{video_quality}.mp4"
        target_video_url = videos and videos.get('preferred_video', {}) and videos.get('preferred_video', {}).get('url', '')
        download_video(target_video_url, ds_file_path)


def write_data_structures_course_data_file(ds_course_data_folder_path):
    ds_course_data = get_ds_course_data()
    ds_course_data_file_path = ds_course_data_folder_path / DATA_STRUCTURES_CRASH_COURSE_DATA_FILE_NAME
    write_python_object_to_file(ds_course_data, ds_course_data_file_path, INDENTATION_SPACES)
    return ds_course_data


def create_data_structures_course_data_folder():
    dsa_course_data_folder_path = pathlib.Path(PARENT_DIR / DATA_STRUCTURES_CRASH_COURSE_FOLDER)
    dsa_course_data_folder_path.mkdir(parents=True, exist_ok=True)
    return dsa_course_data_folder_path


if __name__ == "__main__":
    main()
