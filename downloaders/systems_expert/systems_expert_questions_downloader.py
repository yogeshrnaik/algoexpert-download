import os
import pathlib

import requests

from config import REQUEST_HEADERS_FOR_ALGOEXPERT_SITE, PARENT_DIR, INDENTATION_SPACES
from file_helper import write_python_object_to_file
from question_solution.question_solution_video_downloader import get_video_urls, download_video


SYSTEM_EXPERT_QUESTIONS_ENDPOINT = "https://prod.api.algoexpert.io/api/problems/v1/systemsexpert/design-questions/list"
SYSTEM_EXPERT_QUESTIONS_FOLDER = 'system_expert_questions'
SYSTEM_EXPERT_QUESTIONS_DATA_FILE_NAME = 'system_expert_questions_data.json'


def get_system_expert_questions_data(url=SYSTEM_EXPERT_QUESTIONS_ENDPOINT):
    response = requests.post(url, headers=REQUEST_HEADERS_FOR_ALGOEXPERT_SITE)
    return response.json()


def write_system_expert_questions_data_file(system_expert_questions_data_folder_path):
    system_expert_questions_data = get_system_expert_questions_data()
    system_expert_questions_data_file_path = system_expert_questions_data_folder_path / SYSTEM_EXPERT_QUESTIONS_DATA_FILE_NAME
    write_python_object_to_file(system_expert_questions_data, system_expert_questions_data_file_path, INDENTATION_SPACES)
    return system_expert_questions_data


def create_system_expert_questions_data_folder():
    system_expert_questions_data_folder_path = pathlib.Path(PARENT_DIR / SYSTEM_EXPERT_QUESTIONS_FOLDER)
    system_expert_questions_data_folder_path.mkdir(parents=True, exist_ok=True)
    return system_expert_questions_data_folder_path


def main():
    video_quality = '540p'
    system_expert_questions_data_folder_path = create_system_expert_questions_data_folder()
    system_expert_questions_data = write_system_expert_questions_data_file(system_expert_questions_data_folder_path)
    for idx, question in enumerate(system_expert_questions_data['questions'], 1):
        serial_number = f"{idx}".rjust(2, '0')
        videos = get_video_urls(question['video']['vimeoId'], video_quality)
        sdq_file_path = system_expert_questions_data_folder_path / f"{serial_number} {question['name']}_{video_quality}.mp4"
        if os.path.exists(sdq_file_path):
            print(f"Skipping video: [{sdq_file_path}] as it already exists")
            continue
        target_video_url = videos and videos.get('preferred_video', {}) and videos.get('preferred_video', {}).get('url', '')
        download_video(target_video_url, sdq_file_path)


if __name__ == "__main__":
    main()