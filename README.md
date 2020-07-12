[![DeepPoop-CI](https://circleci.com/gh/YTPgen/DeepPoop.svg?style=shield&circle-token=34e5679a4cd6be8e1be9be66e5f7cd0f76490976)](https://app.circleci.com/pipelines/github/YTPgen)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# DeepPoop
GUI and components for generating YTP videos

# First version spec

The first version of DeepPoop should be able to perform the basic functions of
tranforming a video clip into a YTP video with applied effects. It should be
able to:

* Read video files and detect scenes in them
* Find sub-scenes that have appropriate length and content for applying a YTP
  effect
* Feed sub-scenes to an *EffectApplier* that determines an effect to apply and
  returns the transformed sub-scene
* Concatenate transformed YTP scenes into a final video clip
* Save final video clip to video file
* Allow for several parameters to tweak result

## Components

* GUI - For tweaking parameters and choosing video file
* SceneCutter - splits video into scenes and subscenes
* EffectApplier - Applies an appropriate effect to a subscene (might be no effect)
* ytp_effects - Library containing effect implementations
* Generator - Main class responsible for application flow

## Linux installs

```bash
sudo apt-get install build-essential libsndfile1. cmake libsm6 libxext6 libxrender-dev ffmpeg 
```