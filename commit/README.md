# Usage

**Caution: This software need specific hardware!**

- Change `duration` setting in `config.py`
- If you want to save all internal voice data, change `keep_splited_file` to `True`
- Run `python3 -m pip install -r requirements.txt`
- Run `python3 DoA.py` to record voice (into temp.wav)
- Run `python3 main.py`, input your file name, then you can see the answer.

# Sample result

```text
Please input the name of source file: (Directly press ENTER to use temp.wav) 
Loading...
===============
Talker 1: [Error] Baidu API not return the result of voice recognition
Talker 2: 手绘心形龙
Talker 1: 其实每年到了这个时候
Talker 2: 对于咱们中国人来说
Talker 1: 最高兴的事情
Talker 2: 莫过于一家老小其乐融融
Talker 1: 梅坐在一起吃个团圆饭
Talker 2: 家常
Talker 1: 这一年身边的变化
Talker 2: 唉
Talker 1: 身边的变化
Talker 2: 改革开放三十年
Talker 1: 年年都有变化
Talker 2: 而这些变化啊
Talker 1: 老百姓都看得见
Talker 2: 我的
Talker 1: 因为咱们老百姓实实在在感受到变化带给咱们的扶持合适
Talker 2: 收到细微之处
Talker 1: 什么变化呢
Talker 2: 厦门游艇姜昆
```