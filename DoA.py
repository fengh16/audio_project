import pyaudio
import array
import wave
import os
import datetime
from scipy.io.wavfile import read
import matplotlib.pyplot as plt
import numpy as np
from gcc_phat import gcc_phat

sampleRate = 44100
chunk_duration = 200
FRAME_SIZE = sampleRate // (1000 // chunk_duration)

SOUND_SPEED = 340.0

MIC_DISTANCE_4 = 0.081
MAX_TDOA_4 = MIC_DISTANCE_4 / float(SOUND_SPEED)
duration = 40
chunks = round(duration * (1000 / chunk_duration))


def guess(theta):
    if np.abs(theta[0]) < np.abs(theta[1]):
        if theta[1] > 0:
            best_guess = (theta[0] + 360) % 360
        else:
            best_guess = (180 - theta[0])
    else:
        if theta[0] < 0:
            best_guess = (theta[1] + 360) % 360
        else:
            best_guess = (180 - theta[1])

        best_guess = (best_guess + 270) % 360

    best_guess = (-best_guess + 120) % 360

    return best_guess


def get_direction_array(array_data):
    tau = [0, 0]
    theta = [0, 0]
    pair = [[0, 2], [1, 3]]
    for i, v in enumerate(pair):
        tau[i], _ = gcc_phat(array_data[v[0]], array_data[v[1]], fs=sampleRate, max_tau=MAX_TDOA_4, interp=1)
        theta[i] = np.arcsin(tau[i] / MAX_TDOA_4) * 180 / np.pi
    return guess(theta)


def get_direction_raw(raw_data):
    tau = [0, 0]
    theta = [0, 0]
    pair = [[0, 2], [1, 3]]

    buf = np.fromstring(raw_data, dtype='int16')
    for i, v in enumerate(pair):
        tau[i], _ = gcc_phat(buf[v[0]::4], buf[v[1]::4], fs=sampleRate, max_tau=MAX_TDOA_4, interp=1)
        theta[i] = np.arcsin(tau[i] / MAX_TDOA_4) * 180 / np.pi

    return guess(theta)


def record_thread(device_index, filename, nchannels, duration):
    data = array.array('h')
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=nchannels,
                    rate=sampleRate,
                    input_device_index=device_index,
                    input=True,
                    frames_per_buffer=FRAME_SIZE,
                    )
    wf = wave.open(filename + '.wav', 'wb')
    wf.setframerate(sampleRate)
    wf.setnchannels(nchannels)
    wf.setsampwidth(2)
    stream.start_stream()
    data_len = 0
    print("[{}]".format(os.getpid()), 'record start', datetime.datetime.now())
    while stream.is_active():
        raw_data = stream.read(FRAME_SIZE)

        data.frombytes(raw_data)
        data_len += FRAME_SIZE
        if data_len >= sampleRate * duration:
            break
    print("[{}]".format(os.getpid()), 'record finished', datetime.datetime.now())
    stream.stop_stream()
    wf.writeframes(data.tobytes())
    wf.close()
    p.terminate()


def get_seeed_device_index():
    d = pyaudio.PyAudio()
    for i in range(d.get_device_count()):
        # print(d.get_device_info_by_index(i))
        if 'seeed' in d.get_device_info_by_index(i)['name']:
            print("Found seeed:", i, d.get_device_info_by_index(i))
            return i


def get_volume(chunk):
    chunk = (chunk[0] - np.mean(chunk[0]))
    return np.sqrt((np.sum(chunk * chunk))) / len(chunk)


def get_volume_raw(raw_data):
    buf = np.fromstring(raw_data, dtype='int16')
    arr = buf[0::4]
    arr = arr - np.mean(arr)
    return np.sqrt((np.sum(arr * arr))) / len(arr)


def analysis(filename):
    fs, data = read(filename)
    data = data.T
    t = np.linspace(0, duration, len(data[0]))
    fig, axs = plt.subplots(3, 1, sharex='col', figsize=(16, 9))
    axs[0].plot(t, data[0])

    vols_t = []
    vols = []
    angles_t = []
    angles = []
    for i in range(chunks):
        chunk = data[:, i * FRAME_SIZE:(i + 1) * FRAME_SIZE]
        vol = get_volume(chunk)
        time = i * FRAME_SIZE / sampleRate
        vols_t.append(time)
        vols.append(vol)
        angle = get_direction_array(chunk)
        angles.append(angle)
        angles_t.append(time)
    axs[1].plot(vols_t, vols)
    axs[2].grid(True)
    axs[2].set_ylim([0, 360])
    axs[2].scatter(angles_t, angles)
    plt.savefig('doa.png')


def real_time(device_index):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=4,
                    rate=sampleRate,
                    input_device_index=device_index,
                    input=True,
                    frames_per_buffer=FRAME_SIZE,
                    )
    stream.start_stream()
    time = 0
    while stream.is_active():
        raw_data = stream.read(FRAME_SIZE)
        time += chunk_duration
        volume = get_volume_raw(raw_data)
        if volume > 2:
            print(time, "\tms --> ", get_direction_raw(raw_data))
    stream.stop_stream()
    p.terminate()


if __name__ == '__main__':
    index = get_seeed_device_index()
    # offline--------------
    record_thread(index, 'temp', 4, duration=duration)
    # analysis('temp.wav')
    # ----------
    # real_time(index)
