import os

from tqdm import tqdm
import pathlib
import json
import requests

import pathlib
import sys

CURRENT_FILE_PATH = pathlib.Path(__file__).absolute()
# Adding parent directory to path in order to import from the added directories
sys.path.append(str(CURRENT_FILE_PATH.parent.parent))
sys.path.append(str(CURRENT_FILE_PATH.parent.parent.parent))

# Importing from the directories added to path earlier
from rename import make_file_name_valid
from question_directory_getter import get_question_dir
from file_helper import load_json_file_as_python_obj
from config import VIDEO_URLS_REGEX, REQUEST_HEADERS_FOR_VIMEO_SITE, \
    PARENT_DIR, QUESTION_LIST_FILE_NAME


# https://player.vimeo.com/video/{ VIMEO_VIDEO_ID }
def get_video_urls(video_id: str, preferred_quality: str = None):
    url = f"https://player.vimeo.com/video/{video_id}"
    response = requests.get(url, headers=REQUEST_HEADERS_FOR_VIMEO_SITE)
    content = response.text

    all_videos = []
    preferred_video = None
    for match in VIDEO_URLS_REGEX.finditer(content):
        video = match.groupdict()
        all_videos.append(video)

        if video['quality'] == preferred_quality and preferred_quality is not None:
            preferred_video = video

    return {"videos": all_videos, "preferred_video": preferred_video}


def download_video(url: str, destination: pathlib.Path, chunk_size=1024 * 1024 * 2):
    """Read 1 MB at a time from server to local memory and write to file"""
    print(f"Downloading to {destination} from {url}")
    video_stream = requests.get(url, stream=True)
    total_size_in_bytes = int(video_stream.headers.get('content-length', 0))
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
    with open(destination, 'wb') as video_file:
        for chunk in video_stream.iter_content(chunk_size=chunk_size):
            progress_bar.update(len(chunk))
            video_file.write(chunk)
        progress_bar.close()


def main():
    download_question_solutions(
        "",
        1, 150
    )
    download_question_solutions(
        "",
        151, 195
    )


def download_question_solutions(all_questions_parent_path, questionStartIndex, questionsEndIndex):
    questions: list = \
    load_json_file_as_python_obj(pathlib.Path(rf"{all_questions_parent_path}/" + QUESTION_LIST_FILE_NAME))['questions']
    questions.sort(key=lambda obj: obj.get('difficulty'))
    quality = '540p'

    for idx, question in enumerate(questions, 1):
        if idx < questionStartIndex or idx > questionsEndIndex:
            continue

        question_name = question['name']
        question_file_name = make_file_name_valid(question_name)

        question_dir = get_question_dir(question_name, idx, pathlib.Path(all_questions_parent_path))
        question_solution_path = question_dir / f'{question_file_name}_solution_{quality}.mp4'
        target_video_url = get_target_video_url(question_file_name, quality, question_dir)

        if os.path.exists(question_solution_path):
            print(f"Skipping video: [{question_solution_path}] as it already exists")
        elif target_video_url:
            download_video(target_video_url, question_solution_path)
        else:
            print(f"Skipping video: [{question_solution_path}] as target_video_url is not found")


def get_target_video_url(question_file_name, quality, question_dir):
    question_data_path = question_dir / f'{question_file_name}_data.json'
    with open(question_data_path, 'r') as qd:
        # Load question data from downloaded question meta data
        question_data = json.load(qd)
        video_id = question_data['video']['vimeoId']
    # Get link to download video
    videos = get_video_urls(video_id, preferred_quality=quality)
    # print(f"Video: {videos}")
    target_video_url = videos and videos.get('preferred_video', {}) and videos.get('preferred_video', {}).get('url', '')
    return target_video_url


if __name__ == "__main__":
    main()
