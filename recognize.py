from pocketsphinx import AudioFile
from pydub.silence import split_on_silence
from pydub import AudioSegment

if __name__ == '__main__':
    audio = AudioFile(audio_file='2.wav')
    sound = AudioSegment.from_file('2.wav', format='wav')
    chunks = split_on_silence(sound, min_silence_len=700,silence_thresh=-70)
    for phrase in audio:
        print(phrase.segments(detailed=True)) # => "[('forward', -617, 63, 121)]"
