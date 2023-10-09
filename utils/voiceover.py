import pyttsx3
from TTS.api import TTS
from gtts import gTTS
import torch
import torchaudio

""" This was one of the explored TTS methods.
 It is not used in the final product."""


voiceoverDir = "assets/Voiceovers"

def create_voice_over(fileName, text):
    filePath = f"{voiceoverDir}/{fileName}.wav"

    tts = TTS('tts_models/en/vctk/vits')
    tts.tts_to_file(text=text,  speaker='p230', language=tts.languages, file_path=filePath)

    return filePath

def create_ssml_voiceover(fileName, ssml_prompts):
    language = 'en'
    model_id = 'v3_en'
    device = torch.device('mps')

    model, example_text = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                        model='silero_tts',
                                        language=language,
                                        speaker=model_id)
    model.to(device) 
    sample_rate = 48000
    speaker = 'en_103'
    paths=[]
    for idx, p in enumerate(ssml_prompts):
        path_out = f"{voiceoverDir}/{fileName}_{idx}.wav"
        audio = model.save_wav(ssml_text=p,
                                speaker=speaker,
                                sample_rate=sample_rate,
                                audio_path=path_out)
        paths.append(path_out)
    return paths