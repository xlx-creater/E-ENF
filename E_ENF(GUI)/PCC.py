##Pearson correlation coefficient
import numpy as np # 导入一个数据处理模块
import copy
from scipy.stats import pearsonr
from TDMF import TDMF
# #######IFtest为录音文件ENF
# #######ENFdata为参考信号ENF
def PCC(ConstFs, AStepSize, ENFData, IFtest, AWindowLength):
    ENFData       = np.array(ENFData)
    RecordLength  = len(IFtest)
    ENFLength     = len(ENFData)
    OverFact = AStepSize / ConstFs
    Calibrated = np.ones(ENFLength-RecordLength)
    if ENFLength >= RecordLength:
        for i in range(ENFLength-RecordLength):
            IF0          = ENFData[i: i+RecordLength]
            TempIF1      = copy.copy(IFtest)
            TempIF1      = np.array(TempIF1)
            Calibrated[i]=pearsonr(IF0,TempIF1)[0]    #比较变化趋势相似程度，计算皮尔逊相关系数
            #bbb              = IF0-TempIF1
            #MSECalibrated[i] = np.linalg.norm(bbb)/RecordLength
        m  = Calibrated
        # ### 寻找最小值下标
        min_score = m[0]
        min_index1    = 0
        for ii in range(ENFLength-RecordLength):
            if m[ii] > min_score:
            #if m[ii] < min_score:
                min_score     = m[ii]
                min_index1    = ii

        FinalIndex = min_index1

        StartTimeIndex = int(OverFact * FinalIndex)
        MaxScore = max(Calibrated)
        EndTimeIndex = int(StartTimeIndex + OverFact * RecordLength - OverFact)
        StartSec = int(StartTimeIndex % 60)
        StartMin = (StartTimeIndex - StartSec) / 60
        EndSec = int(EndTimeIndex % 60)
        EndMin = (EndTimeIndex - EndSec) / 60
        CalibratedIF = ENFData[FinalIndex: FinalIndex+RecordLength]

    return CalibratedIF, StartMin, StartSec, EndMin, EndSec, StartTimeIndex, EndTimeIndex, MaxScore