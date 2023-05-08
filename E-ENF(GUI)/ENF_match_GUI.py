import tkinter as tk
from tkinter.filedialog import askdirectory
import soundfile as sf
import numpy as np
from scipy import signal
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from TDMF import TDMF
from find_reference_wav_filename import date_wav_filename
from AccurateSTFT import AccurateSTFT
from scipy.stats import pearsonr
from DV_data import event_files_sampling
# #####################################################
# ################ Generate task

# ################
def Select_file():
    global filenames
    filenames = askdirectory()
    file.set(filenames)

def Select_reference_path():
    global folernames
    folernames = askdirectory()
    path.set(folernames)


# ###########################################start program button############################

def start_program_button():

    ConstFs = 1000
    AWindowLength = 16 * ConstFs
    AStepSize = ConstFs
    NFFT = 200 * ConstFs

    # #####################################################
    file_path = filenames

    FILENAME = filenames.split('/')[-2]
    ENF_Year = FILENAME[7:11]
    ENF_Month = FILENAME[12:14]
    ENF_date_Begin = ENF_date_End = FILENAME[15:17]
    ENF_Hour_Begin = FILENAME[18:20]
    ENF_Hour_End = str(int(FILENAME[18:20]) + 1)
    ENF_second = int(FILENAME[21:23]) * 60 + int(FILENAME[24:26])
    Ref_filename = date_wav_filename(ENF_Year, ENF_Month, ENF_date_Begin, ENF_date_End, ENF_Hour_Begin, ENF_Hour_End)
    Reference = folernames + '/' + Ref_filename + '.wav'
    data_ref, frequency = sf.read(Reference)


    Use_data = event_files_sampling(file_path, ConstFs)


    ##### 100Hz
    b, a = signal.butter(4, [(98 * 2 / ConstFs), (102 * 2 / ConstFs)], 'bandpass')   #6
    data_after_fir = signal.filtfilt(b, a, Use_data)
    IFtest1 = np.array(AccurateSTFT(data_after_fir, AWindowLength, AStepSize, ConstFs, NFFT))
    IFtest1 = np.array(TDMF(IFtest1, 21, 0.02))


    IF = IFtest1 / 2


    if len(IF) + ENF_second > 3600:
        Ref_filename2 = date_wav_filename(ENF_Year, ENF_Month, ENF_date_Begin, ENF_date_End,
                                          str(int(ENF_Hour_Begin) + 1), str(int(ENF_Hour_End) + 1))
        Reference2 = folernames + '/' + Ref_filename2 + '.wav'
        data_ref2, frequency = sf.read(Reference2)
        data_ref = np.append(data_ref, data_ref2)

    ### Reference ENF
    ConstFs2 = frequency
    AWindowLength2 = 16 * ConstFs2
    AStepSize2 = ConstFs2
    NFFT2 = 200 * ConstFs2
    IF_ref_total = AccurateSTFT(data_ref, AWindowLength2, AStepSize2, ConstFs2, NFFT2)

    IF_ref = IF_ref_total[ENF_second:ENF_second + len(IF)]

    corr = pearsonr(IF, IF_ref)[0] * 100
    MAE = np.sum(np.absolute(IF - IF_ref)) / len(IF)

    titlename='Similiraty:  ' + '%0.2f' % corr + '%' + '    ' + 'MAE: ' + '%f' %MAE


    # ####################### Drawing
    matplotlib.use('TkAgg')
    fig = plt.Figure(figsize=(5, 4), dpi=80)
    draw_set = FigureCanvasTkAgg(fig, master=window)
    ax = fig.add_subplot(111)
    ax.plot(IF, label='record')
    ax.legend(loc='upper right')
    ax.plot(IF_ref, label='reference')
    ax.legend(loc='upper right')
    ax.set_ylim(49.95, 50.05)
    ax.set(title=titlename, ylabel='Frequency (Hz)', xlabel='Time (s)')
    fig.savefig(FILENAME + '.eps',dpi=80,format='eps',bbox_inches = 'tight')
    draw_set.get_tk_widget().place(x=100, y=100, height=420, width=480)


# ####################################################  window
window = tk.Tk()
window.title('Event-based ENF (E-ENF)')
window.geometry('680x550')

# ##################################################### GUI



pixelVirtual = tk.PhotoImage(width=1, height=1)

#
btn = tk.Button(window, text="Unpacked Events :", image=pixelVirtual, height = 20, width = 140, compound="c", command=Select_file)
btn.place(x=15, y=20)
file = tk.StringVar()
folder = tk.Entry(window, textvariable=file)
folder.place(x=170, y=23, width=420)


btn2 = tk.Button(window, text="ENF_Reference Folder :", image=pixelVirtual, height = 20, width = 140, compound="c", command=Select_reference_path)
btn2.place(x=15, y=55)
path = tk.StringVar()
folder = tk.Entry(window, textvariable=path)
folder.place(x=170, y=58, width=420)


# Program run button
start_pro = tk.Button(window, text="Start", image=pixelVirtual, height = 50, width = 50, compound="c", command=start_program_button)
start_pro.place(x=600, y=22)
window.mainloop()
