import numpy as np #进行科学计算的基础软件包
from scipy.fftpack import fft   #Scipy是一个用于数学、科学、工程领域的常用软件包，可以处理插值、积分、优化、图像处理、常微分方程数值解的求解、信号处理等问题。
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def AccurateSTFT (Signal,Window,StepPoints,Fs,NFFT):
   FrameSize       = Window
   Signal2         = np.zeros(int(FrameSize/2)*2 + len(Signal))
   Signal2[int(FrameSize/2):int(FrameSize/2)+len(Signal)] = Signal
   WindowPositions = range(1, len(Signal2) - int(FrameSize)+2, StepPoints)
   IF0             = np.zeros(len(WindowPositions))

   # f, t, X = sc.signal.stft(Signal[0:256], fs=Fs, window='hann', nperseg=256, noverlap=None, nfft=256)
   # Y = np.array(fft(sc.signal.windows.hann(256)*Signal[0:256], 256))
   # Sx=X[:, 0]
   # Sy=Y[0:257]
   # plt.subplot(121)
   # plt.plot(abs(Sx))
   #
   # plt.subplot(122)
   # plt.plot(abs(Sy))
   # plt.title('FFT of Mixed wave(two sides frequency range)', fontsize=7, color='#7A378B')  # 注意这里的颜色可以查询颜色代码表

   #plt.show()

   for i in range(len(WindowPositions)):
      B                     = np.array(fft(Signal2[WindowPositions[i]:WindowPositions[i] + int(FrameSize)], NFFT))
      HalfTempFFT           = B[:int(len(B)/2)]
      absHalfTempFFT        = abs(HalfTempFFT)
      PeakLoc               = np.argmax(absHalfTempFFT)
      ValueLeft             = HalfTempFFT[PeakLoc - 1]
      ValueCenter           = HalfTempFFT[PeakLoc]
      ValueRight            = HalfTempFFT[PeakLoc + 1]
      lalalal               = (ValueRight - ValueLeft)/(2*ValueCenter - ValueRight - ValueLeft)
      CorrectionCoef        = -lalalal.real
      IF0[i]                = (PeakLoc + CorrectionCoef - 1) * Fs / NFFT
   return IF0
