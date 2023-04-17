import cv2
import tkinter as tk
from tkinter.filedialog import askdirectory
import soundfile as sf
from scipy import signal
from tkinter import filedialog
import os
import time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from TDMF import TDMF
from find_reference_wav_filename import date_wav_filename
from AccurateSTFT import AccurateSTFT
from PCC import PCC
from scipy.stats import pearsonr
from DV_data import event_files_sampling,event_files_delta_sampling
from harmonic_select import harmonic_select
import librosa
# #####################################################  函数定义
# ################ Generate task 显示用户设定的搜索时间范围
def show_task_time():
    global ENF_Year
    global ENF_Month
    global ENF_date_Begin
    global ENF_date_End
    global ENF_Hour_Begin
    global ENF_Hour_End
    ENF_Year             =entry_Year.get()
    ENF_Month            =entry_Month.get()
    ENF_date_Begin       =entry_date_begin.get()
    ENF_date_End         =entry_date_end.get()
    ENF_Hour_Begin       =entry_hour_begin.get()
    ENF_Hour_End         =entry_hour_end.get()

    Begin_time = '    Begin:'+ENF_Year+'/'+ENF_Month+'/'+ENF_date_Begin+'/'+ENF_Hour_Begin+'\n'
    End_time   = '    END:' + ENF_Year+'/'+ENF_Month+'/'+ENF_date_End+'/'+ENF_Hour_End+'\n'
    in_data_text.insert('insert', 'Targeted time interval:\n')
    in_data_text.insert('insert', Begin_time)
    in_data_text.insert('insert', End_time)
# ################录音文件选择
def Select_file():
    global filenames
    filenames = askdirectory()
    file.set(filenames)

def Select_reference_path():
    global folernames
    folernames = askdirectory()
    path.set(folernames)


def select_max_region(mask):
    nums, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    background = 0
    for row in range(stats.shape[0]):
        if stats[row, :][0] == 0 and stats[row, :][1] == 0:
            background = row
    stats_no_bg = np.delete(stats, background, axis=0)
    max_idx = stats_no_bg[:, 4].argmax()
    max_region = np.where(labels==max_idx+1, 1, 0)

    return max_region
# ###########################################start program button############################

# ########################################### 按键 #############################

def start_program_button():

    ConstFs = 1000
    AWindowLength = 16 * ConstFs
    AStepSize = ConstFs
    NFFT = 200 * ConstFs

    ConstFs2 = 400
    AWindowLength2 = 16 * ConstFs2
    AStepSize2 = ConstFs2
    NFFT2 = 200 * ConstFs2

    # #####################################################  文件处理
    start_time = time.time()
    file_path = filenames
    events_path = os.path.abspath(os.path.dirname(file_path))


    Use_data = event_files_sampling(file_path, ConstFs)
    # Use_data =event_files_delta_sampling(file_path, ConstFs)


    np.save("Data/Save_data.npy", Use_data)


    # ##### 谐波选择
    # k = 4     #谐波次数
    # StepPoints = 10      #频率步进
    # IFtest1 = harmonic_select(Use_data, StepPoints, k, AWindowLength, AStepSize, ConstFs, NFFT)


    ##### 100Hz基频
    b, a = signal.butter(4, [(98 * 2 / ConstFs), (102 * 2 / ConstFs)], 'bandpass')   #6
    data_after_fir = signal.filtfilt(b, a, Use_data)
    IFtest1 = np.array(AccurateSTFT(data_after_fir, AWindowLength, AStepSize, ConstFs, NFFT))
    IFtest1 = np.array(TDMF(IFtest1, 21, 0.02))


    IFtest = IFtest1 / 2


    record_len = len(IFtest)*ConstFs2

    # ###  参考信号文件名获取  函数find_reference_wav_filename

    # #######################################读取参考信号文件并匹配##########
    refrence_file_name   = folernames + '/'
    storeFileStrings     = date_wav_filename(ENF_Year, ENF_Month, ENF_date_Begin, ENF_date_End, ENF_Hour_Begin, ENF_Hour_End)
    len_of_File          = int(len(storeFileStrings)/23)

    StartMin         = [None]*len_of_File
    StartSec         = [None]*len_of_File
    EndMin           = [None]*len_of_File
    EndSec           = [None]*len_of_File
    MaxScore         = [None]*len_of_File

    CalibratedIF   = [[None]*len(IFtest) for i in range(len_of_File)]
    StartTimeIndex = [None]*len_of_File
    EndTimeIndex   = [None]*len_of_File

    count_wav_not_exist = 0

    for ii in range(len_of_File):
        filename_wav=refrence_file_name+storeFileStrings[ii*23 : ii*23+23] +'.wav'

        if os.path.exists(filename_wav):
            data_ref, frequency= sf.read(filename_wav)

            if ii < len_of_File - 1:
                filename_wav2 = refrence_file_name + storeFileStrings[ii * 23 + 23: ii * 23 + 46] + '.wav'
                if os.path.exists(filename_wav2):
                    ccc = np.zeros((len(data_ref) + record_len))
                    data_ref_add, frequency = sf.read(filename_wav2)
                    ccc[:len(data_ref)] = data_ref
                    ccc[len(data_ref): len(data_ref) + record_len] = data_ref_add[:record_len]
                else:
                    ccc = np.zeros( len(data_ref))
                    ccc[:len(data_ref)] = data_ref
            else:
                ccc = np.array(data_ref)
            # atime=time.time()
            IF = AccurateSTFT(ccc, AWindowLength2, AStepSize2, ConstFs2, NFFT2)
            # btime=time.time()
            CalibratedIF[ii], StartMin[ii], StartSec[ii], EndMin[ii], EndSec[ii], StartTimeIndex[ii], EndTimeIndex[ii], MaxScore[ii]= \
                PCC(ConstFs, AStepSize, IF, IFtest, AWindowLength)

        else:
            output_str = storeFileStrings[ii*23 : ii*23+23]+' not exist\n'  # 若参考信号不存在则输出文件not exist
            in_data_text.insert('insert', output_str)
            count_wav_not_exist = count_wav_not_exist+1
            continue

    # ########### 若文件不全为空
    if len_of_File > count_wav_not_exist:
        # ####################### 找出最小值对应位置
        max_index = MaxScore.index(max(MaxScore))

        find_filename = storeFileStrings[max_index*23: max_index*23+23]
        begin_hour = int(find_filename[15:17]) - 1
        begin_day_str = find_filename[8:10]
        if begin_hour < 0:
            begin_hour = 24 + begin_hour
            begin_day = int(begin_day_str) - 1
            begin_day_str = '%02d' % begin_day

        begin_hour_str = '%02d' % begin_hour

        if EndTimeIndex[max_index] >= 3600:
            end_hour = begin_hour+1
            end_hour_str = '%02d' % end_hour
        else:
            end_hour_str = begin_hour_str

        # ####################### 输出估算的录制时间
        StartMin_str = '%02d' % StartMin[max_index]
        StartSec_str = '%02d' % StartSec[max_index]
        EndMin_str   = '%02d' % EndMin[max_index]
        EndSec_str   = '%02d' % EndSec[max_index]

        in_data_text.insert('insert', '\nEstimated timestamp:\n')
        Date_estimated = 'Date:  ' + find_filename[0:4] + '/' + ENF_Month + '/' + begin_day_str + '\n'
        in_data_text.insert('insert', Date_estimated)
        time_begin = 'Begin time:  '+begin_hour_str+' : ' + StartMin_str + ' : ' + StartSec_str + '\n'
        time_end   = 'End time  :  ' + end_hour_str + ' : ' + EndMin_str + ' : ' + EndSec_str + '\n'
        in_data_text.insert('insert', time_begin)
        in_data_text.insert('insert', time_end)

        IF_find = CalibratedIF[max_index]


        IFtest = IFtest + np.mean(IF_find) - np.mean(IFtest)  ##########直接搬移########
        IFtest = np.clip(IFtest, 50-0.05, 50+0.05)
        corr1 = pearsonr(IFtest, IF_find)[0]*100

        MSE = np.sum((IFtest - IF_find) ** 2) / len(IFtest)
        MAE = np.sum(np.absolute(IFtest-IF_find))/len(IFtest)
        in_data_text.insert('insert', 'Similiraty:')
        in_data_text.insert('insert', '%0.2f' % corr1)
        in_data_text.insert('insert', '%\n')
        titlename='Similiraty:  ' + '%0.2f' % corr1 + '%' + '    ' + 'MAE: ' + '%f' %MAE + '    ' + 'MSE: ' + '%f' %MSE


        np.save("Data/Event.npy", IFtest)
        # np.savetxt("Event.txt", IFtest, fmt='%f', delimiter='\n')
        #
        np.save("Data/IF_ref.npy", IF_find)
        # np.savetxt("IF_ref.txt", IF_find, fmt='%f', delimiter='\n')


        # ####################### 绘图
        matplotlib.use('TkAgg')
        fig = plt.Figure(figsize=(5, 4), dpi=80)  # 设置空画布fig，figsize为大小，dpi为分辨率
        draw_set = FigureCanvasTkAgg(fig, master=window)  # 将空画布设置在tkinter上
        ax = fig.add_subplot(111)  # 设置坐标轴
        ax.plot(IF_find, label='reference')  # 绘制参考信号图像
        ax.legend(loc='upper right')
        ax.plot(IFtest, label='record')  # 绘制录制信号图像
        ax.legend(loc='upper right')
        # ax.plot(IF_true, label='true')  # 绘制图像
        # ax.legend(loc='upper right')
        # ax.set_xlim(0, 630)
        ax.set_ylim(49.95, 50.05)
        ax.set(title=titlename, ylabel='Frequency (Hz)', xlabel='Time (s)')
        fig.savefig('scatter.eps',dpi=80,format='eps',bbox_inches = 'tight')
        draw_set.get_tk_widget().place(x=280, y=100, height=420, width=480)  # 将画好的画布放置在tkinter界面上
        end_time = time.time()
        total_time = '%0.2f' %(end_time-start_time)
        in_data_text.insert('insert', 'elapsed time:')
        in_data_text.insert('insert', total_time)
        in_data_text.insert('insert', '\n')
    else:
        # ####################### 绘制录音文件波形
        matplotlib.use('TkAgg')
        fig = plt.Figure(figsize=(5, 4), dpi=80)  # 设置空画布fig，figsize为大小，dpi为分辨率
        draw_set = FigureCanvasTkAgg(fig, master=window)  # 将空画布设置在tkinter上
        ax = fig.add_subplot(111)  # 设置坐标轴
        ax.plot(IFtest, label='record')  # 绘制录制信号图像
        ax.legend(loc='upper right')
        ax.set( ylabel='Frequency (Hz)', xlabel='Time (s)')
        fig.savefig('scatter.eps',dpi=80,format='eps',bbox_inches = 'tight')
        draw_set.get_tk_widget().place(x=280, y=100, height=420, width=480)  # 将画好的画布放置在tkinter界面上
        in_data_text.insert('insert', 'None of the files exist')
        in_data_text.insert('insert', '\n')


# ####################################################  window
window = tk.Tk()
window.title('ENF Matching GUI')
window.geometry('800x550')

# ##################################################### GUI界面设计

# 设计用户选择搜索的时间范围
tk.Label(window, text='Possible begin and end time of recording').place(x=20, y=100)

# year
tk.Label(window, text='Year(e.g.,2018): ').place(x=50, y=130)
entry_Year=tk.Entry(window, width=5)
entry_Year.place(x=150, y=130)
# month
tk.Label(window, text='Month(1-12):').place(x=50, y=170)
entry_Month=tk.Entry(window, width=5)
entry_Month.place(x=150, y=170)
# date
tk.Label(window, text='Date(1-31):').place(x=50, y=210)
entry_date_begin = tk.Entry(window, width=3)
entry_date_begin.place(x=140, y=210)
entry_date_end = tk.Entry(window, width=3)
entry_date_end.place(x=180, y=210)
# hour
tk.Label(window, text='Hour(0-23):').place(x=50, y=250)
entry_hour_begin = tk.Entry(window, width=3)
entry_hour_begin.place(x=140, y=250)
entry_hour_end = tk.Entry(window, width=3)
entry_hour_end.place(x=180, y=250)

# 文件输出框
tk.Label(window, text='Open File :').place(x=65, y=25)
btn = tk.Button(window, text="Browser", command=Select_file)
btn.place(x=140, y=20)
file = tk.StringVar()
folder = tk.Entry(window, textvariable=file)
folder.place(x=210, y=25, width=550)

# 参考信号文件夹获取框
tk.Label(window, text='Reference Folder :').place(x=20, y=60)
btn2 = tk.Button(window, text="Browser", command=Select_reference_path)
btn2.place(x=140, y=55)
path = tk.StringVar()
folder = tk.Entry(window, textvariable=path)
folder.place(x=210, y=60, width=550)

# 任务范围获取框
generate_task = tk.Button(window, text="Generate Task", command=show_task_time).place(x=20, y=280)
in_data_text=tk.Text(window, width=30, height=15)
in_data_text.place(x=20, y=320)

# 程序运行按键
start_pro = tk.Button(window, text="Start Processing", command=start_program_button).place(x=130, y=280)
         
window.mainloop()

