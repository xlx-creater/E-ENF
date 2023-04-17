##最小均方误差分析
import numpy as np # 导入一个数据处理模块
import copy
from TDMF import TDMF
# #######IFtest为录音文件ENF
# #######ENFdata为参考信号ENF
def MMSE(ConstFs, AStepSize, ENFData, IFtest, AWindowLength):
    ENFData       = np.array(ENFData)
    RecordLength  = len(IFtest)
    ENFLength     = len(ENFData)
    OverFact = AStepSize / ConstFs
    MSECalibrated = np.ones(ENFLength-RecordLength)
    if ENFLength >= RecordLength:
        for i in range(ENFLength-RecordLength):
            IF0          = ENFData[i: i+RecordLength]
            TempIF1      = copy.copy(IFtest)
            TempIF1      = np.array(TempIF1)
            bbb              = IF0-TempIF1
            MSECalibrated[i] = np.linalg.norm(bbb)/RecordLength
        m  = MSECalibrated
        # ### 寻找最小值下标
        min_score = m[0]
        min_index1    = 0
        for ii in range(ENFLength-RecordLength):
            if m[ii] < min_score:
                min_score     = m[ii]
                min_index1    = ii

        FinalIndex = min_index1

        StartTimeIndex = int(OverFact * FinalIndex)
        MinScore = min(MSECalibrated)
        EndTimeIndex = int(StartTimeIndex + OverFact * RecordLength - OverFact)
        StartSec = int(StartTimeIndex % 60)
        StartMin = (StartTimeIndex - StartSec) / 60
        EndSec = int(EndTimeIndex % 60)
        EndMin = (EndTimeIndex - EndSec) / 60
        CalibratedIF = ENFData[FinalIndex: FinalIndex+RecordLength]

    return CalibratedIF, StartMin, StartSec, EndMin, EndSec, StartTimeIndex, EndTimeIndex, MinScore