import numpy as np
import copy

# #######IFtest is the estimated ENF
# #######ENFdata is the reference ENF
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
        # ### Find the minimum index
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