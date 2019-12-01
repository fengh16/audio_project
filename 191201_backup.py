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


def get_text_ans(data):
    temp_file_name = str(time.time()) + 'a.wav'
    downsampleWav(data, temp_file_name)
    ans = get_wav_ans(temp_file_name, lang='ch')
    os.remove(temp_file_name)
    return ans


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
    angles_people = []  # the angle of everyone
    angles_raw_data_people = []  # the raw data of angles of everyone
    data_people = []  # the files of everyone
    last_data = None
    prev_last_data = None
    last_angle = None
    prev_last_angle = None
    last_angle_index = None
    prev_last_angle_index = None
    last_used = True
    prev_last_used = True

    # vols_t = []
    # vols = []
    # angles_t = []
    # angles = []
    # ans = None
    for i in range(chunks):
        chunk = data[:, i * FRAME_SIZE:(i + 1) * FRAME_SIZE]
        vol = get_volume(chunk)
        # time_now = i * FRAME_SIZE / sampleRate
        # vols_t.append(time_now)
        # vols.append(vol)
        angle = get_direction_array(chunk)
        if vol < vol_least_threshold:
            angle = None
        if angle is None:
            if last_angle_index is not None and len(data_people[last_angle_index]) > 0:
                print(4)
                print('用户%d说%s' % (last_angle_index, get_text_ans(data_people[last_angle_index][-1])))
            prev_last_angle = last_angle
            prev_last_data = last_data
            prev_last_used = last_used
            prev_last_angle_index = last_angle_index
            last_angle = angle
            last_data = chunk[1:2, :]
            last_used = False
            last_angle_index = None
            continue
        len_people = len(angles_people)
        found_similar = False
        found_index = None
        for j in range(len_people):
            if angle_similar(angles_people[j], angle):
                found_similar = True
                angles_raw_data_people[j].append(angle)
                angles_people[j] = sum(angles_raw_data_people[j]) / len(angles_raw_data_people[j])
                found_index = j
                break
        if not found_similar:
            found_index = len_people
            angles_people.append(angle)
            angles_raw_data_people.append([angle])
            data_people.append([])
        single = chunk[1:2, :]
        if not last_used:  # Last chunk not used, so we need to append this to now data
            if last_data is not None:
                single = np.append(last_data, single)  # 把上一次的搞到了这一次这里
            data_people[found_index].append(single)
            if last_angle_index is not None and len(data_people[last_angle_index]) > 0:
                print(1)
                print('用户%d说%s' % (last_angle_index, get_text_ans(data_people[last_angle_index][-1])))
        elif last_angle_index == found_index:
            data_people[found_index][-1] = np.append(data_people[found_index][-1], single)
        else:
            data_people[found_index].append(single)
            if last_angle_index is not None and len(data_people[last_angle_index]) > 0:
                print(2)
                print('用户%d说%s' % (last_angle_index, get_text_ans(data_people[last_angle_index][-1])))
        # Change all data
        prev_last_angle = last_angle
        prev_last_data = last_data
        prev_last_used = last_used
        prev_last_angle_index = last_angle_index
        last_angle = angle
        last_data = single
        last_used = True
        last_angle_index = found_index
        # angles.append(angle)
        # # angles_t.append(time_now)
        # print(time_now, angle)
        # single = chunk[1:2, :]
        # ans = np.append(ans, single) if ans is not None else single
    # print(ans.shape)
    # # save_wav(ans, 'aaaaaa')
    # temp_file_name = str(time.time()) + 'a.wav'
    # downsampleWav(ans, temp_file_name)
    # print(get_wav_ans(temp_file_name, lang='ch'))
    # os.remove(temp_file_name)
    if last_angle_index is not None and len(data_people[last_angle_index]) > 0:
        print(3)
        print('用户%d说%s' % (last_angle_index, get_text_ans(data_people[last_angle_index][-1])))


if __name__ == '__main__':
    analysis('temp.wav')
    # WiFi-Test
    # 12345678
    # pi:raspberry