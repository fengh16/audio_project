import pyAudioAnalysis.audioSegmentation as au


if __name__ == '__main__':
    a = au.speakerDiarization('2.wav', 2, mt_size=0.3, mt_step=0.05, st_win=0.05)
    print(a)