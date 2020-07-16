[![DeepPoop-CI](https://circleci.com/gh/YTPgen/DeepPoop.svg?style=shield&circle-token=34e5679a4cd6be8e1be9be66e5f7cd0f76490976)](https://app.circleci.com/pipelines/github/YTPgen)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# DeepPoop
GUI and components for generating YTP videos

## Quickstart

```bash
# Run generator with parameters
python generate.py --video_file=my_clip.mp4 \
--scene_threshold=70 \
--subscene_threshold=40 \
--length=15 \
--max-intensity=70 \
--reuse=False \
--abruptness=0.1 \
generate
```

### Parameters

* **`video_file`**: Path to video file
* **`scene_threshold`**: Threshold at which to split video clip into scenes *(0-100)*
* **`subscene_threshold`**: Threshold at which to split scenes into subscenes that effects are applied to *(0-100)*
* **`length`**: Total length of final video in seconds (Final length cannot not be longer than original if **`reuse`** is set to **`False`**)
* **`scene_min_len`**: Minimum length in frames of a scene - Default: **`600`**
* **`subscene_min_len`**: Minimum length in frames of a subscene - Default: **`90`**
* **`abruptness`**: How likely a scene is to end after each subscene *(0-1)* - Default: **`0.2`**
* **`reuse`**: Whether to allow reuse of same scenes - Default: `True`
* **`max_intensity`**: Maximum intensity of final video. Intensity controls which effects are applied, how often and how many - Default: **`20`**
* **`easy_start`**: Sets an initial intensity to allow for a gentle start - Default: **`0`**
* **`downscale`**: Downscale factor when performing scene detection. If not specified detect value automatically 

## Components

* GUI - For tweaking parameters and choosing video file
* SceneCutter - splits video into scenes and subscenes
* EffectApplier - Applies an appropriate effect to a subscene (might be no effect)
* Generator - Main class responsible for application flow

## Linux installs

```bash
sudo apt-get install build-essential libsndfile1. cmake libsm6 libxext6 libxrender-dev ffmpeg 
```

## Effect Previews

To preview what happens when applying an effect with certain parameters `effect_preview.py` can be used. Just pass the name of the effect and any necessary parameters for `Effect` initialization.

### Example

```bash
# First argument is name of the effect (case sensitive) and second is the strength 0-1 followed by any kwargs of the effect
python effect_preview.py Rotate 0.2 --min_speed=0.5 --max_speed=3
# Strength can be emitted for a value of 1 by default
python effect_preview.py Rotate --min_speed=0.5 --max_speed=3
```