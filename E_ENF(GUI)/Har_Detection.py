import numpy as np #进行科学计算的基础软件包
from scipy.fftpack import fft   #Scipy是一个用于数学、科学、工程领域的常用软件包，可以处理插值、积分、优化、图像处理、常微分方程数值解的求解、信号处理等问题。
from scipy import signal
from AccurateSTFT import AccurateSTFT
from TDMF import TDMF



###########波动程度寻找谐波#############
def harmonic_detection(data, k, AWindowLength, AStepSize, ConstFs, NFFT, TH, Freq_bounds):       #寻找k次谐波

    b, a = signal.butter(4, [(98 * 2 / ConstFs), (102  * 2 / ConstFs)], 'bandpass')
    Signal_k = signal.filtfilt(b, a, data)
    IF1 = np.array(AccurateSTFT(Signal_k, AWindowLength, AStepSize, ConstFs, NFFT))
    IF1 = np.array(TDMF(IF1, 21, 0.02))
    # IF1 = IF1 / 2

    Mask = np.ones(len(IF1))
    IF_Diff = np.diff(IF1)
    IF_Diff = np.insert(IF_Diff, 0, 0)

    Detect_tem1 = np.argwhere(np.abs(IF_Diff) > TH)
    Mask[Detect_tem1] = 0
    Detect_tem2 = np.argwhere(IF1 >= (50 + Freq_bounds))
    Mask[Detect_tem2] = 0
    Detect_tem3 = np.argwhere(IF1 <= (50 - Freq_bounds))
    Mask[Detect_tem3] = 0

    if (Mask == 1).all():
        return IF1
    else:
        IF_total = [[] for k in range(k)]  # 保存k次谐波
        for j in range(k):  # 分别得到k次谐波分量
            b, a = signal.butter(4, [(((98 + j * 100)) * 2 / ConstFs), ((102 + j * 100) * 2 / ConstFs)], 'bandpass')
            Signal_k = signal.filtfilt(b, a, data)
            IFtest1 = np.array(AccurateSTFT(Signal_k, AWindowLength, AStepSize, ConstFs, NFFT))
            IFtest1 = np.array(TDMF(IFtest1, 21, 0.02))
            IF_total[j] = IFtest1 / (j + 1)

        IF_total = np.array(IF_total)
        IF = IF1
        size_clip_shift = int((AWindowLength / AStepSize) // 2)

        for ind in np.argwhere(Mask==0):
            ind = ind[0]
            Score = [10 for j in range(k)]
            for j in range(k):
                if ind>=size_clip_shift:
                    IF[ind-size_clip_shift:ind+size_clip_shift] = IF_total[j,ind-size_clip_shift:ind+size_clip_shift]
                elif ind<size_clip_shift and ind+size_clip_shift<(len(np.where(Mask==0))):
                    IF[:ind+size_clip_shift] = IF_total[j,:ind+size_clip_shift]

                IFtest_Diff = np.diff(np.array(IF[:ind+size_clip_shift]))
                Score[j] = np.sum(np.abs(IFtest_Diff))
            min_index = Score.index(min(Score))

            if ind >= size_clip_shift:
                IF[ind - size_clip_shift:ind + size_clip_shift] = IF_total[min_index, ind - size_clip_shift:ind + size_clip_shift]
            elif ind < size_clip_shift and ind + size_clip_shift < (len(np.where(Mask == 0))):
                IF[:ind + size_clip_shift] = IF_total[min_index, :ind + size_clip_shift]
        return IF