from newspaper import Article, ArticleException
from newsapi import NewsApiClient
import os
from news.get_ai_content import get_prompt_from_script, get_pictures_from_script
import random as rand
from utils.videoscript import VideoScript
import configparser
from moviepy.editor import *

def get_headlines(num):
    config = configparser.ConfigParser()
    config.read('config.ini')
    news_key = config["Video"]["news_api"]

    newsapi = NewsApiClient(api_key=news_key)
    top_headlines = newsapi.get_top_headlines(category='business', country='us')
    news_summary = []
    for i in range(0, min(num, top_headlines['totalResults'])):
        try:
            summary = get_summary(top_headlines['articles'][i]['url'])
        except ArticleException:
            print('Failed to get article')
            num+=1
            continue
        news_script = {'summary':summary, 'title':top_headlines['articles'][i]['title']}
        news_summary.append(news_script)
        if i == num-1:
            break
    return news_summary

def get_summary(url):
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()
    return article.summary

def create_news(num):
    """This generated still image videos from the news api and gpt."""
    config = configparser.ConfigParser()
    config.read('config.ini')
    #get the script
    script = get_headlines('business', num)
    #get the prompt
    prompt, message = get_prompt_from_script(script)

    #Try parsing the prompt if it fails retry twice
    try:
        gpt_script = eval(prompt)
    except:
        print("Could not parse prompt, 1st retry")
        try:
            prompt, message = get_prompt_from_script(script)
            gpt_script = eval(prompt)
        except:
            print("Could not parse prompt, 2nd retry")
            prompt, message = get_prompt_from_script(script)
            gpt_script = eval(prompt)
    
    #get the images
    id = rand.randint(0, 100000)
    image_path = get_pictures_from_script(gpt_script, id)
    content = VideoScript("google.com", "news_vid", id)

    #create the video
    failedAttempts = 0
    for num, i in enumerate(gpt_script):
        script_key = ""
        for j in i.keys():
            if "script" in j:
                script_key = j
        if(content.addCommentScene(i[script_key], f'{id}_{num}')):
            failedAttempts += 1
        if (content.canQuickFinish() or (failedAttempts > 2 and content.canBeFinished())):
            break

    clips = []
    marginSize = 0
    for num,comment in enumerate(content.frames):
        clips.append(__createClip(image_path[num], comment.audioClip, marginSize))

    contentOverlay = concatenate_videoclips(clips).set_position(("center", "center"))

    # Compose background/foreground
    final = CompositeVideoClip(
        clips=[contentOverlay], 
        size=(608, 1080)).set_audio(contentOverlay.audio)
    final.duration = content.getDuration()
    final.set_fps(30)

    # Write output to file
    print("Rendering final video...")
    bitrate = config["Video"]["Bitrate"]
    threads = config["Video"]["Threads"]
    outputFile = f"news/outputVideos/{id}.mp4"
    print(outputFile)
    final.write_videofile(
        outputFile, 
        codec='libx264', 
        audio_codec='aac', 
        temp_audiofile='temp-audio.m4a', 
        remove_temp=True,
        threads = threads, 
        bitrate = bitrate
    )



def __createClip(screenShotFiles, audioClip, marginSize):
        clips = [ImageSequenceClip([i], durations=[audioClip.duration/4]).set_position(("center", "center")) for i in screenShotFiles]
        imageClip = concatenate(clips)
        imageClip = imageClip.resize(width=(608-marginSize))
        videoClip = imageClip.set_audio(audioClip)
        videoClip.fps = 1
        return videoClip


if __name__ == "__main__":
    create_news(2)