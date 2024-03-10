import asyncio
import concurrent.futures
import glob
import json
import shutil
import subprocess
import time
import uuid
import logging
import urllib
from pathlib import Path
from typing import Iterable, List, Dict
import re
from urllib.request import urlretrieve

import replicate
import requests

logging.basicConfig(
    filename="debug.log",  # Specify the file name for logging
    level=logging.DEBUG,  # Set the desired logging level
    format="%(asctime)s - %(levelname)s - %(message)s",
)



def generate_prompt(previous_frame: str,
                    current_frame: str,
                    next_frame: str) -> str:
    """
    Takes in the previous, current, and next frame descriptions, and generates a cohesive prompt.
    :param previous_frame:
    :param current_frame:
    :param next_frame:
    :return:
    # Example usage
    prev_frame = "a man is sitting on a bench in a park"
    curr_frame = "the same man takes a drink of water from a bottle"
    next_frame = "the man stands up and starts walking away from the bench"

    prompt = generate_prompt(prev_frame, curr_frame, next_frame)
    print(prompt)

    """

    prompt = ""
    print(previous_frame, next_frame, current_frame)
    # Check if previous_frame is provided
    if previous_frame:
        prompt += f"Continuing from the previous frame where {previous_frame}, "

    # Add current_frame description
    prompt += f"the current frame shows {current_frame}. "

    # Check if next_frame is provided
    if next_frame:
        prompt += f"In the next frame, {next_frame}."

    return prompt


def generate_payload(prompt_parts: Iterable[str],
                     params: dict = None) -> dict:
    params = params if params else {}
    DEFAULT_PARAMS = {
        "num_frames": 24,
        "fps": 12,
        "width": 576,
        "height": 320,
        "guidance_scale": 12.5,
        "num_inference_steps": 50,
        "model": "576w",
        "negative_prompt": "blurry, text, watermark, logo, worst quality, low quality",
    }
    if params:
        data = DEFAULT_PARAMS.update(params)
    else:
        data = DEFAULT_PARAMS
    print(data, prompt_parts)
    data["prompt"] = generate_prompt(*prompt_parts)
    return data


def default_payload(**kwargs):
    default_params = {
        "seed": -1,
        "steps": 25,
        "width": 256,
        "frames": 640,
        "height": 384,
        "context": 16,
        "clip_skip": 2,
        "scheduler": "k_dpmpp_sde",
        "base_model": "majicmixRealistic_v5Preview",
        "output_format": "mp4",
        "guidance_scale": 9,
        "negative_prompt": "blurry, text, watermark, logo, worst quality, low quality, ghost, spooky, halloween.",
        "prompt_fixed_ratio": 0.5,
        "custom_base_model_url": "",
        "playback_frames_per_second": 8
    }
    # Update default parameters with provided values
    default_params.update(kwargs)
    return default_params

def better_payload():
    return default_payload(
        steps=30,
        guidance_scale=20,
        context=20,
        playback_frames_per_second=4
    )



def generate_replicate_payload(sequence_payload, **kwargs):
    data = default_payload(**kwargs)
    data.update({
        'head_prompt': sequence_payload.get('head_prompt'),
        'prompt_map': sequence_payload.get('prompt_map'),
        'tail_prompt': sequence_payload.get('tail_prompt'),
        'frames': sequence_payload.get('frame_count')
    })
    print(data)
    return data

def download_result(fname, url, check_name=False):
    response = requests.get(url, stream=True)
    fname = slugify(fname)
    fdir = Path(fname) / "output"

    fname = f"{fname}.mp4"

    with open(fname, mode="wb") as file:
        for chunk in response.iter_content(chunk_size=10 * 1024):
            file.write(chunk)
    return fname

import os
def send_to_replicate(film, payload, download=False):

    output = replicate.run(
        "zsxkib/animatediff-prompt-travel:1b8a8f2725c03b1ff4a0b960079899131c384149d1feba45e4ef43653deb3b5f",
        input=payload,

    )
    if download:
        try:
            download_result(film, output, check_name=True)
        except Exception as e:
            print(e)
    return output

def replicate_sample():
    input_data = {
        "seed": -1,
        "steps": 25,
        "width": 256,
        "frames": 640,
        "height": 384,
        "context": 16,
        "clip_skip": 2,
        "scheduler": "k_dpmpp_sde",
        "base_model": "majicmixRealistic_v5Preview",
        "head_prompt": "Surreal, afro-futurism, dark, sci-fi, drama, art-film, art.",
        "prompt_map": "0: Surreal depiction of a disheveled apartment, with our protagonist a black teenager and "
                      "the local patriarch engaged in cryptic conversation, objects morphing and shifting around "
                      "them The black teenager and the local patriarch engaged in conversation, disheveled "
                      "apartment background | 32: Objects in the room start to morph and shift, creating a "
                      "surreal atmosphere | 64: Close-up of the teenager\'s face, showing confusion and disbelief "
                      "| 96: Freeze-frame of the black teenager\'s widened eyes, indicating realization | 128: "
                      "Transition from the disheveled apartment to the lush jungle landscape | 160: Shots of the "
                      "black teenager navigating through dense foliage, pursued by unseen forces | 192: Discovery "
                      "of ancient ruins and mystical phenomena hidden within the jungle | 224: Introduction of "
                      "the feminine face watching from the shadows | 256: Return to the modern cityscape, "
                      "with the black teenager lying on the ground after being hit by a bus | 288: Flashbacks to "
                      "moments of disconnect and confusion experienced by the black teenager | 320: Crowd of "
                      "onlookers and paramedics surrounding the scene of the accident | 352: Reappearance of the "
                      "feminine face amidst the chaos | 384: The protagonist moves away from the stream of souls "
                      "towards the forming face | 416: The tunnel\'s brilliance dims as he approaches the "
                      "enigmatic face | 448: The protagonist\'s eyes beam toward the face, signaling a moment of "
                      "connection | 480: Camera pans out to show the protagonist\'s decisive choice to turn away "
                      "from the light. The protagonist\'s decisive choice to turn away from the light, embracing a "
                      "new path forward",
        "tail_prompt": "The aesthetic blends surreal, occult, and metaphysical visuals to create an atmosphere "
                       "that is both unsettling and beautiful.",
        "output_format": "mp4",
        "guidance_scale": 9,
        "negative_prompt": "blurry, text, watermark, logo, worst quality, low quality, ghost, spooky, halloween.",
        "prompt_fixed_ratio": 0.5,
        "custom_base_model_url": "",
        "playback_frames_per_second": 8
    }
    print(input_data)

    output = replicate.run(
        "zsxkib/animatediff-prompt-travel:1b8a8f2725c03b1ff4a0b960079899131c384149d1feba45e4ef43653deb3b5f",
        input=input_data,

    )
    print(output)


def process_prompt_map(prompts: List[str], frame_count: int = 128, step: int = None) -> str:
    """
    This function takes an iterable of strings, along with optional parameters for frame count and step.
    It then generates a prompt map with each item in the iterable prefixed with the current frame count, separated by |
    The output should look like:
    {frame-number}: {frame-content} | {frame-number}: {frame-content} | etc...
    0: A man standing on a beach | 32: The man starts to walk down the beach

    :param prompts: iterable of prompts
    :param frame_count:
    :param step:
    :return:
    """
    # Check if step is provided
    if step is None:
        # Calculate the step based on the length of the iterable and the frame count
        step = int(frame_count / len(prompts))

    # Ensure that step is divisible by 8
    if step % 8 != 0:
        step = (step // 8) * 8

    # Initialize the frame counter
    frame = 0
    prompt_strings = []

    # Iterate over the iterable and generate prompt strings
    for item in prompts:
        # Construct the prompt string with the current frame and item
        prompt_string = f"{frame}: {item}"
        # Append the prompt string to the list
        prompt_strings.append(prompt_string)
        # Increment the frame counter by the step
        frame += step

    # Join the prompt strings into a single string separated by |
    return " | ".join(prompt_strings)


def split_keyframes_by_sentence(keyframe_prompts: List[dict]) -> List[str]:
    """
    This function returns a list of keyframes by taking each item in the supplied list
    and splitting them by sentence and finally flattening into a single list of keyframes.

    :param keyframe_prompts: iterable of keyframes
    :return: a list of keyframes split by sentence
    """
    import re
    keyframes = []
    for prompt_dict in keyframe_prompts:
        prompt = prompt_dict['description']
        # Split the prompt into sentences
        sentences = re.split(r'[.!?]\s*', prompt)
        # Add each sentence to the keyframes list
        keyframes.extend([s.strip() for s in sentences if s.strip()])
    return keyframes


def process_sequence(sequence_data):
    keyframe_prompts = sequence_data['parts']
    transitions = sequence_data['transitions']
    # Add transitions to keyframe_prompts
    keyframe_prompts = [{'description': transitions['in']}] + keyframe_prompts + [{'description': transitions['out']}]
    # Split keyframes by sentence
    keyframe_prompts = split_keyframes_by_sentence(keyframe_prompts)

    # Process prompt map
    prompt_map = process_prompt_map(keyframe_prompts, frame_count=sequence_data['prompt_map']['frame_count'])

    # Generate film payload
    film_payload = generate_film_payload(sequence_data, keyframe_prompts, prompt_map)

    return film_payload


def generate_film_payload(sequence_data, keyframe_prompts, prompt_map):
    """
    Take the sequence and generate a payload dictionary.
    Payload will contain:
    prompt_map: Prompt for changes in animation. Provide 'frame number : prompt at this frame', separate different prompts with '|'.
                Make sure the frame number does not exceed the length of video (frames)
    head_prompt: Primary animation prompt. This will be prefixed at the start of every individual prompt in the map
    tail_prompt: Additional prompt that will be appended at the end of the main prompt or individual prompts in the map

    :param sequence_data: The sequence data dictionary
    :param keyframe_prompts: List of keyframe prompts
    :param prompt_map: The processed prompt map string
    :return: The film payload dictionary
    """
    payload = {
        'frame_count':sequence_data['prompt_map']['frame_count'],
        'sequence_id': sequence_data['id'],
        'prompt_map': prompt_map,
        'head_prompt': ' '.join(keyframe_prompts[:2]),
        'tail_prompt': sequence_data['action'] + ', ' + sequence_data['visuals'] + ', ' + sequence_data['aesthetic']
    }
    return payload




def slugify(s):
  s = s.lower().strip()
  s = re.sub(r'[^\w\s-]', '', s)
  s = re.sub(r'[\s_-]+', '-', s)
  s = re.sub(r'^-+|-+$', '', s)
  return s


def export_film_payloads(film_payloads: List[Dict], film_name: str):
    """
    Exports the film payloads to a directory structure in the 'data' directory.

    Args:
        film_payloads (List[Dict]): A list of film payload dictionaries.
        film_name (str): The name of the film.

    Returns:
        None
    """
    data_dir = Path('data')
    film_dir = data_dir / slugify(film_name)
    film_dir.mkdir(exist_ok=True)

    sequences_dir = film_dir / 'sequences'
    sequences_dir.mkdir(exist_ok=True)

    for payload in film_payloads:
        sequence_id = payload['sequence_id']
        sequence_id = slugify(sequence_id)
        sequence_file = sequences_dir / f"{sequence_id}.json"
        with open(sequence_file, 'w+') as f:
            json.dump(payload, f, indent=2)




def test_download_result():
    u = "https://replicate.delivery/pbxt/AMnBGuE0NFZRCtAjcx1BCJLjveVL8UcTw36sAlEX1QZL8dPJA/00_4232147101044052450_A-black-teenager-opens-his-eyes-and-finds-himself-.mp4"
    ff = slugify("Disheveled Apartment")
    fname = f"{ff}.mp4"
    download_result(fname, u)
    assert os.path.isfile(fname)

def load_film_payloads(film_name: str) -> List[Dict]:
    """
    Loads the film payloads from the directory structure in the 'data' directory.

    Args:
        film_name (str): The name of the film.

    Returns:
        List[Dict]: A list of film payload dictionaries.
    """
    data_dir = Path('data')
    film_dir = data_dir / slugify(film_name)
    sequences_dir = film_dir / 'sequences'

    film_payloads = []

    for sequence_file in sequences_dir.glob('*.json'):
        with open(sequence_file, 'r') as f:
            payload = json.load(f)
            film_payloads.append(payload)

    return film_payloads


def test_get_replicate_payload():
    film = 'The Tunnel'
    seqs = load_film_payloads(film)
    example = seqs[0]
    tosend = generate_replicate_payload(example)
    print(tosend)
    print(better_payload())


def test_send_to_replicate():
    film = 'The Tunnel'
    seqs = load_film_payloads(film)
    example = seqs[0]
    tosend = generate_replicate_payload(example)
    output = send_to_replicate(film, tosend, download=True) # should be async
    print(output)


def load_and_process_sequences(data_dir='data', fname='sequences.json'):
    # Load JSON data
    data_dir = Path(data_dir)
    sequences_file = data_dir / fname
    with open(sequences_file, 'r') as f:
        data = json.load(f)


    film_payloads = []
    for sequence in data['sequences']:
        film_payload = process_sequence(sequence)
        film_payloads.append(film_payload)


    return data['name'], film_payloads

def test_generate_film_payload():
    name, payloads = load_and_process_sequences()
    print(payloads)

def test_export_film():
    name, payloads = load_and_process_sequences()
    export_film_payloads(payloads, name)
    print(f"exported film {name} \n ")
    l = load_film_payloads(name)
    print(f"Loaded film {name} \n data: \n {l}")


def test_prompt_map():
    # Example usage
    iterable = ["The teenager and the local patriarch engaged in conversation, disheveled apartment background",
                "Objects in the room start to morph and shift, creating a surreal atmosphere",
                "Close-up of the teenager's face, showing confusion and disbelief",
                "Freeze-frame of the teenager's widened eyes, indicating realization"]

    prompt_string = process_prompt_map(iterable)
    print(prompt_string)


def main():
    pass



def test_async_send_all_payloads():
    film = 'The Tunnel'
    seqs = load_film_payloads(film)
    payloads = seqs[2:]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # start the load operations and mark each future with its film index
        future_to_film = {
            executor.submit(
                send_to_replicate,
                payload['sequence_id'],
                payload,
                download=True): film_index for film_index, payload in enumerate(payloads)
        }

        for future in concurrent.futures.as_completed(future_to_film):
            film_index = future_to_film[future]
            try:
                output = future.result()
                print(f'downloaded film {film_index}')
            except Exception as exc:
                print(f'generated film {film_index} with an error: {exc}')

import ffmpeg

def concatenate_videos(input_files, output_file, dir_root=None):
    input_args = []
    if dir_root:
        input_files = [str(Path(dir_root) / i) for i in input_files]
        output_file = Path(dir_root) / output_file
    fl = []
    for file in input_files:
        input_args.extend(['-i', file])
        fl.append(ffmpeg.input(file))
    # video_and_audios_files = [item for sublist in map(lambda f: [f.video, f.audio], fl) for item in sublist]
    with open('concat.txt', 'w') as concat_file:
        concat_file.writelines([('file %s\n' % input_path) for input_path in input_files])
    # ffmpeg -f concat -safe 0 -i concat.txt -c copy output.mp4
    ffmpeg_command = "ffmpeg -f concat -safe 0 -i concat.txt -c copy output.mp4"
    subprocess.call(ffmpeg_command, shell=True, cwd=os.getcwd())
    os.remove("concat.txt")
    return os.path.isfile("output.mp4")


def copy_files(from_dir, to_dir, ext='.mp4'):
    Path(to_dir).mkdir(exist_ok=True)
    for file in os.listdir(from_dir):
        file2 = str(Path(from_dir) / file)
        if file.endswith(ext):
            shutil.copy(file2, to_dir / file)
            print(f"moved {file} to {to_dir}")

def test_make_film_movie():
    """

    :return:
    """
    film = 'The Tunnel'

    # Move all the downloaded mp4s to the output folder
    film_slug = slugify(film)
    film_dir = Path('data') / film_slug


    output_dir = film_dir / "output"

    output_dir.mkdir(exist_ok=True)

    copy_files(output_dir, output_dir / "joined")
    output_dir = output_dir / "joined"

    # Stitch the mp4 files together
    output_file = f'{film_slug}_full.mp4'
    video_file_list = glob.glob(f"{output_dir}/*.mp4")
    worked = concatenate_videos(video_file_list, output_file, dir_root=os.getcwd())
    # ffmpeg_command = f'ffmpeg -i "concat:{str(cmd_dir)}" -c copy {output_file}'
    # print(f"made command {ffmpeg_command}")
    # subprocess.call(ffmpeg_command, shell=True, cwd=cwd)
    if worked:
        print(f"Created {output_file}")
        shutil.move("output.mp4", output_dir)
    else:
        print("failed")



if __name__ == '__main__':
    # prev_frame = "a man is sitting on a bench in a park"
    # curr_frame = "the same man takes a drink of water from a bottle"
    # next_frame = "the man stands up and starts walking away from the bench"
    # payload = generate_payload((prev_frame, curr_frame, next_frame), {})
    # print(payload)
    main()
