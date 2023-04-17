import cv2
import matplotlib
import matplotlib.pyplot as plt
import scipy
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import scipy.signal as signal
from TDMF import TDMF
from AccurateSTFT import AccurateSTFT
import tkinter as tk
from tkinter import filedialog
import numpy as np
import math
from threshold_find import find_threshold
from MUSIC import MUSIC
from ESPRIT import ESPRIT
from DV_data import event2timesurfaces,event2histogram

# ################文件选择
def Select_wav_file():
    global filenames
    filenames = filedialog.askopenfilename()
    file.set(filenames)

def start_program():
    file_path = filenames
    Save_data = event2timesurfaces(file_path , fps=400)
    Save_data2 = event2histogram(file_path , fps=400)
    np.save("Save_data.npy", Save_data)
    np.savetxt("Save_data.txt", Save_data, fmt='%f', delimiter='\n')

    np.save("Save_data2.npy", Save_data2)
    np.savetxt("Save_data2.txt", Save_data2, fmt='%f', delimiter='\n')

    ConstFs =400 #
    AWindowLength = 16*ConstFs
    AStepSize = ConstFs
    NFFT = 200 * ConstFs


    #Save_data = np.load('Save_data.npy')
    #95-105Hz带通滤波器

    b, a = signal.butter(6, [(99 * 2 / ConstFs), (101 * 2 / ConstFs)], 'bandpass')
    data_after_fir = signal.filtfilt(b, a, Save_data)
    IFtest1 = np.array(AccurateSTFT(data_after_fir, AWindowLength, AStepSize, ConstFs, NFFT))  ## STFT
    IFtest1 = np.array(TDMF(IFtest1, 21, 0.02))
    IFtest = IFtest1 / 2
    IFtest = IFtest + 50 - np.mean(IFtest)
    IFtest1 = np.clip(IFtest, 49.8, 50.2)

    data_after_fir2 = signal.filtfilt(b, a, Save_data2)
    IFtest2 = np.array(AccurateSTFT(data_after_fir2, AWindowLength, AStepSize, ConstFs, NFFT))  ## STFT
    IFtest2 = np.array(TDMF(IFtest2, 21, 0.02))
    IF2 = IFtest2/ 2
    IF2 = IF2 + 50 - np.mean(IF2)
    IFtest2 = np.clip(IF2, 49.8, 50.2)

    #画图
    matplotlib.use('TkAgg')
    fig = plt.Figure(figsize=(5, 4), dpi=80)  # 设置空画布fig，figsize为大小，dpi为分辨率
    draw_set = FigureCanvasTkAgg(fig, master=window)  # 将空画布设置在tkinter上
    ax = fig.add_subplot(111)  # 设置坐标轴
    ax.plot(IFtest1, label='timesurfaces')  # 绘制录制信号图像
    ax.plot(IFtest2, label='histogram')
    ax.legend(loc='upper right')
    ax.set(ylabel='Frequency (Hz)', xlabel='Time (s)')
    draw_set.get_tk_widget().place(x=280, y=100, height=420, width=480)  # 将画好的画布放置在tkinter界面上
    fig.savefig('scatter.eps', dpi=80, format='eps', bbox_inches='tight')


# ####################################################  window
window = tk.Tk()
window.title('ENF')
window.geometry('800x550')


# 文件输出框
tk.Label(window, text='Open File :').place(x=65, y=25)
btn = tk.Button(window, text="Browser", command=Select_wav_file)
btn.place(x=140, y=20)
file = tk.StringVar()
folder = tk.Entry(window, textvariable=file)
folder.place(x=210, y=25, width=550)

# 程序运行按键
start_pro = tk.Button(window, text="Start Processing", command=start_program).place(x=80, y=280)

window.mainloop()
