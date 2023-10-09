import whisper_timestamped as whisper #pip3 install git+https://github.com/linto-ai/whisper-timestamped
from difflib import SequenceMatcher
import moviepy.editor as mpy
from moviepy.video.tools.subtitles import SubtitlesClip
from whisper_timestamped.make_subtitles import split_long_segments


def get_sub_timestamps(wav_file, max_length=10):
    audio = whisper.load_audio(wav_file)

    model = whisper.load_model("tiny", device="cpu")

    subtitle_timestamp = whisper.transcribe(model, audio, language="en")
    split_sub = split_long_segments(subtitle_timestamp['segments'], max_length)
    subtitle_timestamp['segments'] = split_sub
    return subtitle_timestamp

def get_sub_video_overlay(subtitles, true_script=None, audio_files=None):
    subtitle_clips = []
    final_clips = []
    if true_script is not None:
        for rem in ['<p>', '</p>', '<s>', '</s>', '<speak>', '</speak>']:
            true_script = [i.replace(rem, '') for i in true_script]
    
    for idx, clip in enumerate(subtitles):
        prev_start = 0
        for i in clip['segments']:
            start = i['start']
            end = i['end']
            if true_script is not None:
                best_m, _ = get_best_match(i['text'], true_script[idx])
            else:
                best_m = i['text']
            if start - prev_start > 0.001:
                subtitle = mpy.TextClip(' ', fontsize=36, color='white', font='Proxima-Nova')
                subtitle = subtitle.set_duration(start - prev_start)
                subtitle_clips.append(subtitle)
            subtitle = mpy.TextClip(best_m, fontsize=36, color='white', font='Montserrat-ExtraBold')
            subtitle = subtitle.set_duration(end - start)
            subtitle_clips.append(subtitle)
            prev_start = end

        if idx < len(subtitles) - 1 and audio_files is not None:
            audio_t = mpy.AudioFileClip(audio_files[idx]).duration
            subtitle = mpy.TextClip(' ', fontsize=36, color='white', font='Proxima-Nova')
            subtitle = subtitle.set_duration(audio_t-subtitles[idx]['segments'][-1]['end'])
            subtitle_clips.append(subtitle)

        if len(subtitle_clips) > 1:
            final_clips.append(mpy.concatenate_videoclips(subtitle_clips))
        else:
            final_clips.append(subtitle_clips[0])
        subtitle_clips=[]

    return final_clips



def get_best_match(query, corpus, step=4, flex=3, case_sensitive=False, verbose=False):
    """Return best matching substring of corpus.

    Parameters
    ----------
    query : str
    corpus : str
    step : int
        Step size of first match-value scan through corpus. Can be thought of
        as a sort of "scan resolution". Should not exceed length of query.
    flex : int
        Max. left/right substring position adjustment value. Should not
        exceed length of query / 2.

    Outputs
    -------
    output0 : str
        Best matching substring.
    output1 : float
        Match ratio of best matching substring. 1 is perfect match.
    """

    def _match(a, b):
        """Compact alias for SequenceMatcher."""
        return SequenceMatcher(None, a, b).ratio()

    def scan_corpus(step):
        """Return list of match values from corpus-wide scan."""
        match_values = []

        m = 0
        while m + qlen - step <= len(corpus):
            match_values.append(_match(query, corpus[m : m-1+qlen]))
            if verbose:
                print(query, "-", corpus[m: m + qlen], _match(query, corpus[m: m + qlen]))
            m += step

        return match_values

    def index_max(v):
        """Return index of max value."""
        return max(range(len(v)), key=v.__getitem__)

    def adjust_left_right_positions():
        """Return left/right positions for best string match."""
        # bp_* is synonym for 'Best Position Left/Right' and are adjusted 
        # to optimize bmv_*
        p_l, bp_l = [pos] * 2
        p_r, bp_r = [pos + qlen] * 2

        # bmv_* are declared here in case they are untouched in optimization
        bmv_l = match_values[p_l // step]
        bmv_r = match_values[p_l // step]

        for f in range(flex):
            ll = _match(query, corpus[p_l - f: p_r])
            if ll > bmv_l:
                bmv_l = ll
                bp_l = p_l - f

            lr = _match(query, corpus[p_l + f: p_r])
            if lr > bmv_l:
                bmv_l = lr
                bp_l = p_l + f

            rl = _match(query, corpus[p_l: p_r - f])
            if rl > bmv_r:
                bmv_r = rl
                bp_r = p_r - f

            rr = _match(query, corpus[p_l: p_r + f])
            if rr > bmv_r:
                bmv_r = rr
                bp_r = p_r + f

            if verbose:
                print("\n" + str(f))
                print("ll: -- value: %f -- snippet: %s" % (ll, corpus[p_l - f: p_r]))
                print("lr: -- value: %f -- snippet: %s" % (lr, corpus[p_l + f: p_r]))
                print("rl: -- value: %f -- snippet: %s" % (rl, corpus[p_l: p_r - f]))
                print("rr: -- value: %f -- snippet: %s" % (rl, corpus[p_l: p_r + f]))

        return bp_l, bp_r, _match(query, corpus[bp_l : bp_r])

    if not case_sensitive:
        query = query.lower()
        corpus = corpus.lower()

    qlen = len(query)

    if flex >= qlen/2:
        print("Warning: flex exceeds length of query / 2. Setting to default.")
        flex = 3

    match_values = scan_corpus(step)
    pos = index_max(match_values) * step

    pos_left, pos_right, match_value = adjust_left_right_positions()

    return corpus[pos_left: pos_right].strip(), match_value