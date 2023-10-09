import moviepy.editor as mpy
from moviepy.editor import concatenate_videoclips, concatenate_audioclips

from news.news import get_headlines
from news.get_ai_content import get_prompt_from_script, get_pictures_from_script
from news.google_interface import init_gdrive, upload_wav, retrieve_npy, run_notebook
from utils.get_timestamp_subtitles import get_sub_video_overlay, get_sub_timestamps

class NewsVideo:
    def __init__(self, script, name):
        self.script = script
        self.name = name
        self.file_paths = None

def create_video(audio_file_paths, background_path="/Users/arnaudbergeron/Desktop/anim/prod_8_2X_30fps.mp4"):
    """ This function creates a video from start to finish."""

    # Get the news headline and generate a script
    script = get_headlines(15)
    prompt = get_prompt_from_script(script, [0, 4, 6])

    with open('prompt.txt', 'w') as f:
        f.write('\n'.join(prompt))
        f.write('|')

    vid = NewsVideo(script, 'prod_8')
    vid.file_paths = audio_file_paths

    drive = init_gdrive()
    upload_wav(drive, vid.file_paths)
    run_notebook()
    retrieve_npy(drive)

    # Create subtitles
    tstamp = [get_sub_timestamps(vid.file_paths[i], 20) for i in range(10)]
    vid_to = get_sub_video_overlay(tstamp, None, vid.file_paths)

    # Create video with audio
    clip = mpy.VideoFileClip(background_path)

    # Add audio
    audio = [mpy.AudioFileClip(i) for i in vid.file_paths]
    retimed_audio = [(tot, tot + i.duration / 2) for i in audio for tot in [0, i.duration / 2]]
    retimed_audio = [(i[0] + 1, i[1] + 1) for i in retimed_audio]
    img_clips = []
    id1 = -1
    id2 = 0

    # Add subtitles correctly to the video to account for intro
    for i in retimed_audio:
        if id1 == -1:
            clip_to = mpy.TextClip(' ', fontsize=36, color='white', font='Proxima-Nova')
        else:
            clip_to = mpy.ImageClip(f'/Users/arnaudbergeron/Desktop/Code/auto_content/assets/bingOutput/{vid.name}_{id1}_{id2}.jpeg')
        clip_to.start = i[0]
        clip_to.end = i[1]
        clip_to.duration = i[1] - i[0]
        clip_to = clip_to.resize((340, 340))
        img_clips.append(clip_to)
        id2 = (id2 + 1) % 2
        if id2 == 0:
            id1 += 1

    # Put everything together
    img_clips = [i.set_pos(('center', 'top')).margin(top=50, opacity=0) for i in img_clips]
    audio = concatenate_audioclips(audio)
    clip = clip.set_audio(audio)
    full_clip = mpy.CompositeVideoClip([clip, concatenate_videoclips(vid_to).set_pos(('center', 'bottom')).margin(bottom=150, opacity=0), concatenate_videoclips(img_clips).set_pos(('center', 'top')).margin(top=50, opacity=0)])

    # Add background audio
    background_audio = mpy.AudioFileClip("/Users/arnaudbergeron/Desktop/start_music.wav")

    # CompositeAudioClip
    full_clip_a = mpy.CompositeAudioClip([full_clip.audio, background_audio])

    # Add background audio to clip as background
    full_clip_2 = full_clip.set_audio(full_clip_a)
    logo_clip = mpy.VideoFileClip('/Users/arnaudbergeron/Desktop/assets/logo_intro_3.mov', has_mask=True).resize(height=380)
    full_clip_3 = mpy.CompositeVideoClip([full_clip_2, logo_clip.set_pos(('center', 'top')).margin(top=150, opacity=0)])

    # Final export
    full_clip_3.write_videofile(f"/Users/arnaudbergeron/Desktop/anim/{vid.name}_out.mp4", codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a')
