import json
import os
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image

data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
scripts_dir = os.path.join(
    os.path.dirname(__file__), "..", "data", "llm_interaction_scripts"
)
user_behaviors_data_file = "user_behaviors_data.json"
user_profiles_data_file = "user_profiles_data.json"
user_interactions_data_file = "user_interactions_data.json"


def download_and_save_image(image_url: str, save_path: Path):
    # Download the image
    image_response = requests.get(image_url)
    img = Image.open(BytesIO(image_response.content))

    # Save the image to the provided path
    save_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    img.save(save_path)


def load_llm_response_data_as_json(response_data: str) -> list[dict]:
    _json_data = []
    try:
        _json_data = json.loads(response_data)
    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
    return _json_data


def save_llm_response_data_to_json(response_data: str, filename: str, data_dir: str):
    os.makedirs(data_dir, exist_ok=True)
    output_path = os.path.join(data_dir, filename)

    json_data = load_llm_response_data_as_json(response_data=response_data)
    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(json_data, json_file, indent=4)


def load_json_array_data(data_dir: str, data_file_name: str) -> list[dict]:
    json_file_path = os.path.join(data_dir, data_file_name)
    with open(json_file_path, "r") as file:
        data = json.load(file)
        return data


def save_llm_response_data_to_python(
    response_data: str, filename: str, scripts_dir: str
):
    os.makedirs(data_dir, exist_ok=True)
    output_path = os.path.join(scripts_dir, filename)

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(response_data)
