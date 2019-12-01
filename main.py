from DoA import *
import wave, audioop
from baidu_aip import get_wav_ans
import time

sampleRate = 44100
vol_least_threshold = 2
angle_diff_threshold = 24
len_threshold = 3

# global variables
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


def get_angle_index(angle):
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
    return found_index


def connect_data(target_earlier, source_later):
    target_earlier['len'] += source_later['len']
    target_earlier['data'] = np.append(target_earlier['data'], source_later['data'])
    target_earlier['vol'] = (target_earlier['vol'] * target_earlier['len'] + source_later['vol'] * source_later['len']
                             ) / (target_earlier['len'] + source_later['len'])


def analysis(filename):
    global angles_people, angles_raw_data_people, data_people, last_data, prev_last_data, last_angle, prev_last_angle,\
        last_angle_index, prev_last_angle_index, last_used, prev_last_used

    fs, data = read(filename)
    data = data.T

    ans_list = []

    for i in range(chunks):
        chunk = data[:, i * FRAME_SIZE:(i + 1) * FRAME_SIZE]
        vol = get_volume(chunk)
        angle = get_direction_array(chunk)
        if vol < vol_least_threshold:
            angle = None
        ans_list.append({
            'person_index': None,
            # 'angle': angle,
            'data': chunk[1, :],
            'text': '',
            'vol': vol,
            'len': 1
        })
        if angle is not None:
            ans_list[-1]['person_index'] = get_angle_index(angle)
    # Remove internal spaces
    len_ans_list = len(ans_list)
    for i in range(len_ans_list - 2, 0, -1):
        if ans_list[i]['person_index'] is None and \
                ans_list[i - 1]['person_index'] is None and \
                ans_list[i + 1]['person_index'] is None:
            ans_list.pop(i)
            len_ans_list -= 1
    # Link all same_person_data
    for i in range(len_ans_list - 1, 0, -1):
        if ans_list[i]['person_index'] == ans_list[i - 1]['person_index']:
            connect_data(ans_list[i - 1], ans_list[i])
            ans_list.pop(i)
            len_ans_list -= 1
        elif i > 1 and ans_list[i - 2]['person_index'] == ans_list[i]['person_index'] and ans_list[i]['len'] > 1:
            connect_data(ans_list[i - 1], ans_list[i])
            ans_list[i - 1]['person_index'] = ans_list[i]['person_index']
            ans_list.pop(i)
            len_ans_list -= 1
    # Attach spaces to voice data
    for i in range(len_ans_list - 1, 0, -1):
        if ans_list[i]['person_index'] is None and ans_list[i - 1]['person_index'] is not None:
            connect_data(ans_list[i - 1], ans_list[i])
            ans_list.pop(i)
            len_ans_list -= 1
        elif ans_list[i]['person_index'] is not None and ans_list[i - 1]['person_index'] is None:
            connect_data(ans_list[i - 1], ans_list[i])
            ans_list[i - 1]['person_index'] = ans_list[i]['person_index']
    # Remove too-short-length data
    for i in range(len_ans_list - 1, -1, -1):
        if ans_list[i]['len'] < len_threshold:
            ans_list.pop(i)
            len_ans_list -= 1
    # Link all same_person_data again
    for i in range(len_ans_list - 1, 0, -1):
        if ans_list[i]['person_index'] == ans_list[i - 1]['person_index']:
            connect_data(ans_list[i - 1], ans_list[i])
            ans_list.pop(i)
            len_ans_list -= 1
    print(ans_list)
    for ans in ans_list:
        print('用户%d说%s' % (ans['person_index'], get_text_ans(ans['data'])))


if __name__ == '__main__':
    analysis('temp.wav')
