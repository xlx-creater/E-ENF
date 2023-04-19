##Pearson correlation coefficient
import numpy as np
import copy
from scipy.stats import pearsonr
from TDMF import TDMF
# #######IFtest is the estimated ENF
# #######ENFdata is the reference ENF
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
            Calibrated[i]=pearsonr(IF0,TempIF1)[0]

        m  = Calibrated
        # ### Find the minimum index
        min_score = m[0]
        min_index1    = 0
        for ii in range(ENFLength-RecordLength):
            if m[ii] > min_score:
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