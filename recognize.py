from pocketsphinx import AudioFile
from pydub.silence import split_on_silence
from pydub import AudioSegment
import baidu_aip
import pyAudioAnalysis.audioSegmentation as au
import json

audio_file='2.wav'

def get_name(count):
    return str(count) + "temp.wav"


# 众数 https://blog.csdn.net/yongh701/article/details/50296869
def get_mode(arr):
    arr_appear = dict((a, arr.count(a)) for a in arr)  # 统计各个元素出现的次数
    for k, v in arr_appear.items():  # 否则，出现次数最大的数字，就是众数
        if v == max(arr_appear.values()):
            return k


if __name__ == '__main__':
    sound = AudioSegment.from_file(audio_file, format='wav')
    print('totally' + str(len(sound)) + 'ms')
    chunks = split_on_silence(sound, min_silence_len=300, silence_thresh=-70)
    for c in chunks:
        print(c.duration_seconds)
    chunks = [i for i in chunks if i.duration_seconds > 0.5]
    count = 0
    for c in chunks:
        with open(get_name(count), 'wb') as f:
            c.export(f, 'wav')
        count += 1

    # # print(audio.n_frames())  # 没用
    # audio = AudioFile(audio_file=audio_file)
    # print('Result from pocketsphinx:')
    # for phrase in audio:
    #     segments = phrase.segments(detailed=True) # => "[('forward', -617, 63, 121)]"
    #     if len(segments) == 0:
    #         continue
    #     print(segments)
    #     print('\tStart&End', segments[0][2], segments[-1][3])

    print("BAIDU:")
    selected_chunks = []
    for t in range(len(chunks)):
        ans = baidu_aip.get_wav_ans(get_name(t))
        if 'result' in ans:
            print('\t' + str(t) + '\t' + '\t'.join(ans['result']))
            selected_chunks.append({
                'chunk': chunks[t],
                'result': '\t'.join(ans['result']),
                'time': chunks[t].duration_seconds,
                'person': 0
            })  # 所有有识别结果的都放到了这里

    total = AudioSegment.silent(0)
    start_list = []
    for t in range(len(selected_chunks)):
        dur = selected_chunks[t]['time']
        start_list.append(int(total.duration_seconds + 0.5) * 2)
        total = total.append(selected_chunks[t]['chunk'], 0)
        selected_chunks[t].pop('chunk')
        print('length after added: ', total.duration_seconds)
        total = total.append(AudioSegment.silent((int(total.duration_seconds + 1.6) - total.duration_seconds)* 1000), 0)
        print('length after added silent: ', total.duration_seconds)
    start_list.append(int(total.duration_seconds + 0.5) * 2)
    total.export(get_name('linked'), 'wav')
    recognize_ans = list(au.speakerDiarization(get_name('linked'), 2, mt_size=0.5, mt_step=0.5, st_win=0.1))
    for i in range(len(start_list) - 1):
        selected_chunks[i]['person'] = str(int(get_mode(recognize_ans[start_list[i]: start_list[i + 1]])))
    with open('ans.json', 'w') as f:
        json.dump(selected_chunks, f)
    print(selected_chunks)
