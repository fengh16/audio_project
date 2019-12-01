from DoA import *
import wave, audioop
from baidu_aip import get_wav_ans
import time

sampleRate = 44100
vol_least_threshold = 2
angle_diff_threshold = 24


def angle_similar(a, b):
    if a is not None and b is not None:
        return -angle_diff_threshold < a - b < angle_diff_threshold
    return False


def save_wav(stream, filename):
    wf = wave.open(filename + '.wav', 'wb')
    wf.setframerate(sampleRate)
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.writeframes(stream.tobytes())
    wf.close()


def downsampleWav(data, dst, inrate=sampleRate, outrate=16000, inchannels=1, outchannels=1):
    try:
        s_write = wave.open(dst, 'wb')
    except:
        print('Failed to open files!')
        return False

    try:
        converted = audioop.ratecv(data, 2, inchannels, inrate, outrate, None)
        if outchannels == 1 and inchannels != 1:
            converted = audioop.tomono(converted[0], 2, 1, 0)
    except:
        print('Failed to downsample wav')
        return False

    try:
        s_write.setparams((outchannels, 2, outrate, 0, 'NONE', 'Uncompressed'))
        s_write.writeframes(converted[0])
    except Exception as e:
        print(e)
        print('Failed to write wav')
        return False

    try:
        s_write.close()
    except:
        print('Failed to close wav files')
        return False

    return True


def analysis(filename):
    fs, data = read(filename)
    data = data.T
    ans = None

    for i in range(chunks):
        chunk = data[:, i * FRAME_SIZE:(i + 1) * FRAME_SIZE]
        vol = get_volume(chunk)
        time_now = i * FRAME_SIZE / sampleRate
        # vols_t.append(time_now)
        # vols.append(vol)
        angle = get_direction_array(chunk)
        if vol < vol_least_threshold:
            angle = None
        if angle is None:
            continue
        single = chunk[1:2, :]
        print(time_now, angle)
        ans = np.append(ans, single) if ans is not None else single
    print(ans.shape)
    temp_file_name = str(time.time()) + 'a.wav'
    downsampleWav(ans, temp_file_name)
    print(get_wav_ans(temp_file_name, lang='ch'))
    os.remove(temp_file_name)


if __name__ == '__main__':
    analysis('temp.wav')
    # WiFi-Test
    # 12345678
    # pi:raspberry