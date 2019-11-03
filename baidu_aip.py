from aip import AipSpeech
import config
import time

""" 你的 APPID AK SK """
APP_ID = config.APP_ID
API_KEY = config.API_KEY
SECRET_KEY = config.SECRET_KEY

client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)


class Language:
    CHINESE=1536
    ENGLISH=1737


# 读取文件
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

last_time = 0


# 识别本地文件
def get_wav_ans(name, dev_pid=0, lang='eng'):
    global last_time
    ans = client.asr(get_file_content(name), 'wav', 16000, {
        'dev_pid': dev_pid if dev_pid else (1737 if lang=='eng' else 1536),
    })
    if time.time() - last_time < 0.2:
        time.sleep(0.2 - (time.time() - last_time))
    last_time = time.time()
    return ans

if __name__ == '__main__':
    print(get_wav_ans('2.wav'))