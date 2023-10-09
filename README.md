# text2vid
Exploration of text to video automated content creation

The goal of this project was to create automated video creation flow.

Here's an example output video:


https://github.com/arnaudbergeron/text2vid/assets/58529583/a9b67f81-168b-493e-a687-1dda1b621204



Here's how the pipeline goes:

-> Script Creation from GPT-4
-> Script to TTS
-> Audio to timestamped subtitles
-> Audio to 3D facial animation
-> 3D facial animation to video via Blender


This project was meant to explore the feasability of such a tool. It is not meant to be a production ready tool.
More work could've been put into making the videos feel more natural but I decided to move on to different projects.

TTS model used: https://github.com/neonbjb/tortoise-tts 
3d facial animation model used: https://github.com/Doubiiu/CodeTalker
Frame interpolation model used: https://github.com/megvii-research/ECCV2022-RIFE
Audio to Timestamp Subtitle model: https://github.com/linto-ai/whisper-timestamped

