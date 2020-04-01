import os
import sys
import time
from ctypes import *
from ctypes import c_voidp
import pyaudio
import wave
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

class Msp:

    def __init__(self):
        pass

    def login(self):
        global dll,login_params
        # 调用动态链接库
        dll = cdll.LoadLibrary(r'D:/sdk/Windows_iat1226_5db02976/bin/msc_x64.dll')
        # 登录参数，apppid一定要和你的下载SDK对应
        login_params = b"appid = 5db02976, work_dir = Windows_iat1226_5db02976."
        ret = dll.MSPLogin(None, None, login_params)

    def isr(self, audiofile, session_begin_params):

        MSP_AUDIO_SAMPLE_FIRST = 1
        MSP_AUDIO_SAMPLE_CONTINUE = 2
        MSP_AUDIO_SAMPLE_LAST = 4
        MSP_REC_STATUS_COMPLETE = 5
        ret = c_int()
        sessionID = c_voidp()
        dll.QISRSessionBegin.restype = c_char_p
        sessionID = dll.QISRSessionBegin(None, session_begin_params, byref(ret))
        #print('QISRSessionBegin => sessionID:', sessionID, '\nret:', ret.value)

        # 每秒【1000ms】  16000 次 * 16 bit 【20B】 ，每毫秒：1.6 * 16bit 【1.6*2B】 = 32Byte
        # 1帧音频20ms【640B】 每次写入 10帧=200ms 【6400B】

        # piceLne = FRAME_LEN * 20
        piceLne = 8000
        epStatus = c_int(0)
        recogStatus = c_int(0)

        wavFile = open('D:/机械臂/xArm-Python-SDK-master-1.2.2/xArm-Python-SDK-master/example/wrapper/xarm6/input2.wav', 'rb')
        wavData = wavFile.read(piceLne)

        ret = dll.QISRAudioWrite(sessionID, wavData, len(wavData), MSP_AUDIO_SAMPLE_FIRST, byref(epStatus),
                                 byref(recogStatus))
        #print('len(wavData):', len(wavData), '\nQISRAudioWrite ret:', ret,'\nepStatus:', epStatus.value, '\nrecogStatus:', recogStatus.value)

        time.sleep(0.1)
        while wavData:
            wavData = wavFile.read(piceLne)
            if len(wavData) == 0:
                break
            ret = dll.QISRAudioWrite(sessionID, wavData, len(wavData), MSP_AUDIO_SAMPLE_CONTINUE, byref(epStatus),
                                     byref(recogStatus))
            #print('len(wavData):', len(wavData), 'QISRAudioWrite ret:', ret, 'epStatus:', epStatus.value, 'recogStatus:', recogStatus.value)
            time.sleep(0.1)
        wavFile.close()
        ret = dll.QISRAudioWrite(sessionID, None, 0, MSP_AUDIO_SAMPLE_LAST, byref(epStatus), byref(recogStatus))
        #print('len(wavData):', len(wavData), 'QISRAudioWrite ret:', ret, 'epStatus:', epStatus.value, 'recogStatus:', recogStatus.value)

        print("\n所有待识别音频已全部发送完毕\n获取的识别结果:")

        # -- 获取音频
        laststr = ''
        counter = 0
        while recogStatus.value != MSP_REC_STATUS_COMPLETE:
            ret = c_int()
            dll.QISRGetResult.restype = c_char_p
            retstr = dll.QISRGetResult(sessionID, byref(recogStatus), 0, byref(ret))
            if retstr is not None:
                laststr += retstr.decode()
            counter += 1
            time.sleep(0.2)
            counter += 1
        ret = dll.QISRSessionEnd(sessionID, '\\0')
        return laststr

    def logout(self):
        ret = dll.MSPLogout()

    def get_audio(self,filepath):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2  # 声道数
        RATE = 8000  # 采样率
        RECORD_SECONDS = 5
        WAVE_OUTPUT_FILENAME = filepath
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        print("*" * 10, "开始录音：请在5秒内输入语音")
        frames = []
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        print("*" * 10, "录音结束\n")

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()


    def XF_text(self,filepath, audio_rate):
        msp = Msp()
        print("登录科大讯飞")
        msp.login()
        print("科大讯飞登录成功")
        session_begin_params = b"sub = iat, ptt = 0, result_encoding = utf8, result_type = plain, domain = iat"
        if 8000 == audio_rate:
            session_begin_params = b"sub = iat, domain = iat, language = zh_cn, accent = mandarin, sample_rate = 16000, result_type = plain, result_encoding = utf8"
        text = msp.isr(filepath, session_begin_params)
        # msp.logout()
        print(text)
        return text

    def run(self):
        input_filename = "input2.wav"  # 麦克风采集的语音输入
        input_filepath = ""  # 输入文件的path
        in_path = input_filepath + input_filename
        filename = 'D:/sdk/input2.wav'
        self.get_audio(in_path)
        res= self.XF_text(filename, 8000)
        return res