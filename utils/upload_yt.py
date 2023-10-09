from youtube_uploader_selenium import YouTubeUploader


def upload_yt(video_path, metadata_path):
    uploader = YouTubeUploader(video_path, metadata_path)
    was_video_uploaded, video_id = uploader.upload()
    assert was_video_uploaded