import wave, audioop, os, time
from DoA import FRAME_SIZE, get_volume, get_direction_array
from scipy.io.wavfile import read
from baidu_aip import get_wav_ans
import numpy as np

sampleRate = 44100
vol_least_threshold = 2
angle_diff_threshold = 24
len_threshold = 3

# global variables
angles_people = []  # the angle of everyone
angles_raw_data_people = []  # the raw data of angles of everyone
people_index_record = {}

from config import keep_splited_file


def angle_similar(a, b):
    if a is not None and b is not None:
        diff = abs(a - b)
        while diff >= 180:
            diff -= 360
        return abs(diff) < angle_diff_threshold
    return False


def get_text_ans(data):
    temp_file_name = str(time.time()) + 'a.wav'
    downsampleWav(data, temp_file_name)
    ans = get_wav_ans(temp_file_name, lang='ch')
    if not keep_splited_file:
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
            # angles_people[j] = sum(angles_raw_data_people[j]) / len(angles_raw_data_people[j])
            found_index = j
            break
    if not found_similar:
        found_index = len_people
        angles_people.append(angle)
        angles_raw_data_people.append([angle])
    return found_index


def connect_data(target_earlier, source_later):
    target_earlier['len'] += source_later['len']
    target_earlier['data'] = np.append(target_earlier['data'], source_later['data'])
    target_earlier['vol'] = (target_earlier['vol'] * target_earlier['len'] + source_later['vol'] * source_later['len']
                             ) / (target_earlier['len'] + source_later['len'])
    # print("%d-%d, %d-%d" % (target_earlier['start'], target_earlier['end'], source_later['start'], source_later['end']))
    # if target_earlier['end'] >= source_later['start']:
    #     print("ERROR")
    target_earlier['end'] = source_later['end']


# Concat string in an array
def concat_str(l):
    if len(l) == 0:
        return ''
    ans = l[0]
    for i in range(1, len(l)):
        ans += '；' + l[i]
    return ans


def get_new_index(index):
    global people_index_record
    if index not in people_index_record:
        people_index_record[index] = len(people_index_record)
    return people_index_record[index] + 1


def analysis(filename):
    global angles_people, angles_raw_data_people
    print("Loading...")

    fs, data = read(filename)
    data = data.T

    ans_list = []

    for i in range(len(data[0]) // FRAME_SIZE):
        chunk = data[:, i * FRAME_SIZE: (i + 1) * FRAME_SIZE]
        vol = get_volume(chunk)
        angle = get_direction_array(chunk)
        if vol < vol_least_threshold:
            angle = None
        ans_list.append({
            'person_index': None,
            'angle': angle,
            'data': chunk[1, :],
            'text': '',
            'vol': vol,
            'len': 1,
            'start': i,
            'end': i
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
        if ans_list[i]['person_index'] is None:
            continue
        elif ans_list[i]['person_index'] == ans_list[i - 1]['person_index']:
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
        need_pop = False
        if ans_list[i]['person_index'] is None and ans_list[i - 1]['person_index'] is not None:
            connect_data(ans_list[i - 1], ans_list[i])
            need_pop = True
        if i + 1 < len_ans_list and ans_list[i + 1]['person_index'] is not None and ans_list[i]['person_index'] is None:
            connect_data(ans_list[i], ans_list[i + 1])
            ans_list[i]['person_index'] = ans_list[i + 1]['person_index']
            need_pop = True
        if need_pop:
            ans_list.pop(i)
            len_ans_list -= 1
    # Remove too-short-length data
    for i in range(len_ans_list - 1, -1, -1):
        if ans_list[i]['len'] < len_threshold or ans_list[i]['person_index'] is None:
            ans_list.pop(i)
            len_ans_list -= 1
    # Link all same_person_data again
    for i in range(len_ans_list - 1, 0, -1):
        if ans_list[i]['person_index'] == ans_list[i - 1]['person_index']:
            connect_data(ans_list[i - 1], ans_list[i])
            ans_list.pop(i)
            len_ans_list -= 1
    # print([[a['angle'], a['person_index']] for a in ans_list])
    print("===============")
    for ans in ans_list:
        try:
            returned = get_text_ans(ans['data'])
            if 'result' not in returned:
                print("Talker %d: [Error] %s" % (get_new_index(ans['person_index']), returned['err_msg']))
            else:
                ans['text'] = concat_str(returned['result'])
                print('Talker %d: %s' % (get_new_index(ans['person_index']), ans['text']))
        except:
            print("Talker %d: [Error] Baidu API not return the result of voice recognition" % (get_new_index(ans['person_index'])))


if __name__ == '__main__':
    filename = input('Please input the name of source file: (Directly press ENTER to use temp.wav) ')
    filename = filename.strip()
    if not filename:
        filename = 'temp.wav'
    analysis(filename)
