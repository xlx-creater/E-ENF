import numpy as np
from scipy.fftpack import fft

def AccurateSTFT (Signal,Window,StepPoints,Fs,NFFT):
   FrameSize       = Window
   Signal2         = np.zeros(int(FrameSize/2)*2 + len(Signal))
   Signal2[int(FrameSize/2):int(FrameSize/2)+len(Signal)] = Signal
   WindowPositions = range(1, len(Signal2) - int(FrameSize)+2, StepPoints)
   IF0             = np.zeros(len(WindowPositions))


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
