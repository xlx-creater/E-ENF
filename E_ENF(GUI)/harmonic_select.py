import numpy as np #进行科学计算的基础软件包
from scipy.fftpack import fft   #Scipy是一个用于数学、科学、工程领域的常用软件包，可以处理插值、积分、优化、图像处理、常微分方程数值解的求解、信号处理等问题。
from scipy import signal
from AccurateSTFT import AccurateSTFT
from TDMF import TDMF


# ###########按照信噪比划分估计权重#############
# def harmonic_select(IF_total,StepPoints,k):       #寻找k次谐波,K<3
#     IF_total = np.array(IF_total)
#     # StepPoints = 10
#     Windowlen = len(IF_total[0])//StepPoints
#     IF = np.ones(len(IF_total[0]))*100
#     # Score = [1 for k in range(k)]
#
#     for i in range(Windowlen):
#         Score = [10 for j in range(k)]
#         # abs_diff = [10 for j in range(k)]
#         weights = np.zeros((1, k))
#         for j in range(k):
#             if (i+1)*StepPoints > len(IF_total[0]):
#                 IF_test = IF_total[j, i * StepPoints:(i + 1) * StepPoints]
#             else:
#                 IF_test = IF_total[j,i*StepPoints:]
#             IFtest_Diff = np.diff(np.array(IF_test))
#             Score[j] = np.sum(list(map(abs, IFtest_Diff.tolist())))  # / len(IFtest_Diff)
#             # Score[j] = np.sum(abs(IFtest_Diff)) / len(IFtest_Diff)
#             weights[0, j] = 1/Score[j]
#             # abs_diff[j]=(max(IF_test)-min(IF_test))
#             # IFtest_Diff
#             if (max(list(map(abs, IFtest_Diff.tolist()))) > 0.1 or (max(IF_test)-min(IF_test))<0.0002):
#                 Score[j] = 10
#                 weights[0, j] = 0
#                 # abs_diff[j] = 10
#         # weights = weights / np.sum(weights, axis=1)
#         # IF[i * StepPoints: i * StepPoints + len(IF_test)] = np.dot(weights, IF_total[:,i * StepPoints: i * StepPoints + len(IF_test)])  #将每一段加权平均
#         # diff_sort = np.argsort(abs_diff)
#         min_index = Score.index(min(Score))   #找最小波动成分
#         print(min_index)
#         IF [i * StepPoints: i * StepPoints + len(IF_test)]= IF_total[min_index,i * StepPoints: i * StepPoints + len(IF_test)]
#
#     return IF



###########波动程度寻找谐波#############
def harmonic_select(data, StepPoints, k, iteration, AWindowLength, AStepSize, ConstFs, NFFT):       #寻找k次谐波
    IF_total = [[] for k in range(k)]    #保存k次谐波
    Formal_index = 0

    for j in range(k):       #分别得到k次谐波分量
        b, a = signal.butter(4, [(((98 + j * 100)) * 2 / ConstFs), ((102 + j * 100) * 2 / ConstFs)], 'bandpass')
        Signal_k = signal.filtfilt(b, a, data)
        IFtest1 = np.array(AccurateSTFT(Signal_k, AWindowLength, AStepSize, ConstFs, NFFT))
        IFtest1 = np.array(TDMF(IFtest1, 21, 0.02))
        IFtest1 = IFtest1 / (j + 1)
        IF_total[j] = IFtest1 - np.mean(IFtest1)

    IF_total = np.array(IF_total)
    IF = np.zeros(len(IF_total[0]))

    Windowlen = len(IF_total[0]) // StepPoints  # 按照时间跨度进行划分
    Windowlen = Windowlen if (len(IF_total[0])%StepPoints) == 0 else  Windowlen+1
    for i in range(Windowlen):       #对k次谐波分量进行评估，并在每个时间切片选择最小的波动
        Score = [10 for j in range(k)]
        # weights = np.zeros((1, k))
        for j in range(k):
            if (i+1)*StepPoints < len(IF_total[0]):
                IF_test = IF_total[j, i * StepPoints:(i + 1) * StepPoints]
            else:
                IF_test = IF_total[j, i*StepPoints:]
            # if i>0:
            #     IF_test = IF_total[j, i * StepPoints-StepPoints//2:(i + 1) * StepPoints+StepPoints//2]
            # else:
            #     IF_test = IF_total[j, i*StepPoints:(i + 1) * StepPoints+StepPoints+StepPoints//2]


            # ## 单一分段 ##
            # IFtest_Diff = np.diff(np.array(IF_test)) #if i==0 else np.diff(np.append(IF[i * StepPoints -StepPoints//2:(i + 1) * StepPoints-StepPoints//2],IF_test))
            # # IF_2Diff = np.diff(IFtest_Diff)
            # # Score[j] = np.sum(list(map(abs, IFtest_Diff.tolist())))  # / len(IFtest_Diff)
            # Score[j] = np.sum(np.abs(IFtest_Diff)) #+ np.sum(np.abs(IF_2Diff)) #np.var(IF_test) #作y2 = x^2 图，并标记此线名为quadratic
            # # weights[0, j] = 1/Score[j]        #计算权重

            # if max(IF_test) - min(IF_test) < 0.0005 or max(IF_test) - min(IF_test) > 0.06 :   #or max(IF_test)-min(IF_test) > 0.05 or max(IF_test) - min(IF_test) < 0.001 or
            #     Score[j] = 10
            # 叠加当前分段 ##
            IF[i * StepPoints: i * StepPoints + len(IF_test)] = IF_test
            IFtest_Diff = np.diff(np.array(IF))# IFtest_Diff = np.diff(np.array(IF[:i * StepPoints + len(IF_test)]))
            # IFtest2Diff = np.diff(IFtest_Diff)
            Score[j] = np.sum(np.abs(IFtest_Diff)) #+ np.sum(np.abs(IFtest2Diff))
            # # if max(IF_test) - min(IF_test) < 0.0005 or max(np.abs(IFtest_Diff)) > 0.02 or max(IF_total[j]) - min(IF_total[j])>0.02:   # or max(IF_test) - min(IF_test) < 0.001 or
            # #     Score[j] = 10
            if  IFtest_Diff !=[] and max(np.abs(IFtest_Diff)) > 0.005:   # or max(IF_test) - min(IF_test) < 0.001 or
                Score[j] = 10
            # if  max(IF_test) - min(IF_test) < 0.0005:
            #     Score[i] = 10
                # weights[0, j] = 0
            # weights = weights / np.sum(weights, axis=1)
            # IF[i * StepPoints: i * StepPoints + len(IF_test)] = np.dot(weights, IF_total[:,i * StepPoints: i * StepPoints + len(IF_test)])  #将每一段加权平均
            # if IFtest_Diff != []:
            #     print('Score:{},Diff:{}, Delta:{}'.format(Score[j],max(np.abs(IFtest_Diff)), max(IF_test) - min(IF_test)))
        min_index = Score.index(min(Score))   #找最小波动成分
        if len(IF_test)<2:
            min_index = Formal_index

        # if (np.mean(IF_total[min_index, i * StepPoints: i * StepPoints + len(IF_test)])-IF[i*StepPoints-1]> 0.005):
        #     min_index=Formal_index

        IF [i * StepPoints: i * StepPoints + len(IF_test)]= \
            IF_total[min_index,i * StepPoints: i * StepPoints + len(IF_test)] #-IF_total[min_index,i * StepPoints] + IF_total[Formal_index,i * StepPoints]
        Formal_index = min_index
        # print(min_index)    #输出每次选择的谐波

    ## 二次迭代 ##
    for iter in range(iteration):
        IF_total = np.vstack((IF_total,IF))
        IF = IF_total[-1]

        Windowlen = (len(IF_total[0])-StepPoints//iteration*(iter+1)) // StepPoints  # 按照时间跨度进行划分
        Windowlen = Windowlen if (len(IF_total[0])-StepPoints//iteration*(iter+1)) % StepPoints == 0 else Windowlen + 1
        for i in range(Windowlen):  # 对k次谐波分量加上第一次的IF估计进行评估，并在每个时间切片选择最小的波动
            Score = [10 for j in range(len(IF_total))]
            # weights = np.zeros((1, k))
            for j in range(len(IF_total)):
                if ((i + 1) * StepPoints+StepPoints//iteration*(iter+1)) <= len(IF_total[0]):
                    IF_test = IF_total[j, i * StepPoints+StepPoints//iteration*(iter+1): (i+1) * StepPoints+StepPoints//iteration*(iter+1)]
                else:
                    IF_test = IF_total[j, i * StepPoints+StepPoints//iteration*(iter+1):]

                # if IF_test == []:
                #     continue
                # ## 单一分段 ##
                # IFtest_Diff = np.diff(np.array(IF_test))  # if i==0 else np.diff(np.append(IF[i * StepPoints -StepPoints//2:(i + 1) * StepPoints-StepPoints//2],IF_test))
                # IF_2Diff = np.diff(IFtest_Diff)
                # # Score[j] = np.sum(list(map(abs, IFtest_Diff.tolist())))  # / len(IFtest_Diff)
                # Score[j] = np.sum(np.abs(IFtest_Diff)) + np.sum(np.abs(IF_2Diff))
                # if max(IF_test) - min(IF_test) < 0.0005 or max(IF_test) - min(IF_test) > 0.06:  # or max(IF_test)-min(IF_test) > 0.05 or max(IF_test) - min(IF_test) < 0.001 or
                #     Score[j] = 10
                # 叠加当前分段 ##
                IF[i * StepPoints+StepPoints//iteration*(iter+1): i * StepPoints+StepPoints//iteration*(iter+1) + len(IF_test)] = \
                    IF_test - IF_test[0] + IF[i * StepPoints+StepPoints//iteration*(iter+1)]
                # IF_test = IF[i * StepPoints: (i+1)* StepPoints +len(IF_test)]
                IF_Diff = np.diff(np.array(IF))
                # IF_2Diff = np.diff(IF_Diff)
                Score[j] = np.sum(np.abs(IF_Diff)) #+ np.sum(np.abs(IF_2Diff))
                if IFtest_Diff != [] and max(np.abs(IFtest_Diff)) > 0.005:  # or max(IF_test) - min(IF_test) < 0.001 or
                    Score[j] = 10
                # if max(IF_test) - min(IF_test) < 0.0005:
                #     Score[i] = 10


            min_index = Score.index(min(Score))  # 找最小波动成分
            if len(IF_test) < 2:
                min_index = Formal_index

            IF[i * StepPoints+StepPoints//iteration*(iter+1): i * StepPoints+StepPoints//iteration*(iter+1) + len(IF_test)] = \
                IF_total[min_index, i * StepPoints+StepPoints//iteration*(iter+1): i * StepPoints+StepPoints//iteration*(iter+1) + len(IF_test)]  -IF_total[min_index,i * StepPoints+StepPoints//iteration*(iter+1)] + IF[i * StepPoints+StepPoints//iteration*(iter+1)]
            Formal_index = min_index

            # print('Interation:%d,Segment:%d,Index:%d'%(iter+1,i,min_index))

    return IF