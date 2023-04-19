# ################Smooth function
import math
def TDMF(Input, Order, Threshold):
    InputLength = len(Input)
    FilteredInput = [None] * InputLength
    Output = [None] * InputLength
    PaddingLength = int((int(Order) - 1) / 2)
    Oneline = [1] * PaddingLength
    PadInput = [Oneline[i] * Input[0] for i in range(PaddingLength)]
    PadInput[PaddingLength:PaddingLength + InputLength] = Input
    PadInput[PaddingLength + InputLength:PaddingLength * 2 + InputLength] = [Oneline[i] * Input[-1] for i in
                                                                             range(PaddingLength)]

    for i in range(InputLength):
        Seg = PadInput[i: i + Order]
        Seg.sort()
        FilteredInput[i] = Seg[math.ceil((Order - 1) / 2)]

    DetrendedInput = [FilteredInput[ii] - Input[ii] for ii in range(InputLength)]
    for i in range(InputLength):
        if abs(DetrendedInput[i]) <= Threshold:
            Output[i] = Input[i]
        else:
            Output[i] = FilteredInput[i]
    return Output


