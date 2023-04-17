'''
@ 读取txt格式的事件数据
'''
import numpy as np
import cv2


# 读取txt格式的事件数据，这个时间数据的时间戳单位是秒
class Event_txt_loader:
    def __init__(self, path):
        self.events = np.loadtxt(path)
        # 事件数据
        self.timestamp = self.events[:, 0]
        self.xpos = np.int32(self.events[:, 1])
        self.ypos = np.int32(self.events[:, 2])
        self.polarity = np.uint32(self.events[:, 3])

        self.size = len(self.timestamp)
        # h = np.max(self.ypos) + 1
        # w = np.max(self.xpos) + 1
        h, w = 260, 346
        self.shape = (h, w) # h, w

        self.begin_time = self.timestamp[0]
        self.final_time = self.timestamp[-1]
        self.delta_t_idx = 0    # 记录当前load_delta_t读取到哪了
        self.done = False

    # 单位：秒
    def load_delta_t(self, delta_t):
        # if delta_t < 1:
        #     raise ValueError("load_delta_t(): delta_t must be at least 1 micro-second: {}".format(delta_t))

        current_time = self.timestamp[self.delta_t_idx]     # 当前的时间戳
        if self.done or current_time + delta_t > self.final_time:
            self.done = True
            return np.empty((0,), dtype=np.uint32)

        finish_time = current_time + delta_t
        finish_idx = np.where(self.timestamp < finish_time)[0][-1]

        # print(self.delta_t_idx, finish_idx)
        events = dict()
        events['t'] = self.timestamp[self.delta_t_idx:finish_idx+1]
        events['x'] = self.xpos[self.delta_t_idx:finish_idx+1]
        events['y'] = self.ypos[self.delta_t_idx:finish_idx+1]
        events['p'] = self.polarity[self.delta_t_idx:finish_idx+1]
        events['size'] = finish_idx - self.delta_t_idx + 1
        self.delta_t_idx = finish_idx + 1
        return events

    # 根据给定时间戳，读取该时间戳的前一段时间的事件，单位：秒
    def load_last_delta_t(self, time, delta_t):
        # assert time <= self.final_time, 'time is out of range! Final time is {}'.format(self.final_time)
        begin_time = time - delta_t
        if begin_time < self.begin_time:
            begin_time = self.begin_time
        if time > self.final_time:
            finish_time = self.final_time
        else:
            finish_time = time
        print(begin_time, finish_time)
        if finish_time <= begin_time:
            events = dict()
            events['size'] = 0
            return events

        begin_idx = np.where(self.timestamp >= begin_time)[0][0]
        finish_idx = np.where(self.timestamp <= finish_time)[0][-1]

        print(begin_idx, finish_idx)
        events = dict()
        events['t'] = self.timestamp[begin_idx:finish_idx + 1]
        events['x'] = self.xpos[begin_idx:finish_idx + 1]
        events['y'] = self.ypos[begin_idx:finish_idx + 1]
        events['p'] = self.polarity[begin_idx:finish_idx + 1]
        events['size'] = finish_idx - begin_idx + 1
        return events

    def files_load_t(self, delta_t, current_time):
        # if delta_t < 1:
        #     raise ValueError("load_delta_t(): delta_t must be at least 1 micro-second: {}".format(delta_t))

        # current_time = self.timestamp[self.delta_t_idx]  # 当前的时间戳
        if self.done or current_time + delta_t > self.final_time:
            self.done = True
            return np.empty((0,), dtype=np.uint32),current_time

        finish_time = current_time + delta_t
        if finish_time < self.begin_time:
            finish_time = self.begin_time
        finish_idx = np.where(self.timestamp <= finish_time)[0][-1]
        sampling_time_finish = self.timestamp[finish_idx]
        sampling_begin_time_index = finish_idx
        while True:
            if (self.timestamp[sampling_begin_time_index] == sampling_time_finish):
                sampling_begin_time_index = sampling_begin_time_index - 1
            else:
                break
        # print(self.delta_t_idx, finish_idx)
        events = dict()
        events['t'] = self.timestamp[sampling_begin_time_index + 1:finish_idx + 1]
        events['x'] = self.xpos[sampling_begin_time_index + 1:finish_idx + 1]
        events['y'] = self.ypos[sampling_begin_time_index + 1:finish_idx + 1]
        events['p'] = self.polarity[sampling_begin_time_index + 1:finish_idx + 1]
        self.delta_t_idx = finish_idx + 1
        current_time = finish_time
        return events, current_time

    def files_load_delta_t(self, delta_t, current_time):
        # if delta_t < 1:
        #     raise ValueError("load_delta_t(): delta_t must be at least 1 micro-second: {}".format(delta_t))

        # current_time = self.timestamp[self.delta_t_idx]  # 当前的时间戳

        begin_index = np.where(self.timestamp >= current_time)[0][0]
        finish_time = current_time + delta_t

        if finish_time < self.begin_time:
            finish_time = self.begin_time

        if self.done or finish_time > self.final_time:
            self.done = True
            finish_idx = np.where(self.timestamp <= finish_time)[0][-1]
            events = dict()
            events['t'] = self.timestamp[begin_index:-1]
            events['x'] = self.xpos[begin_index:-1]
            events['y'] = self.ypos[begin_index:-1]
            events['p'] = self.polarity[begin_index:-1]
            events['size'] = finish_idx - begin_index + 1

        else:
            finish_idx = np.where(self.timestamp <= finish_time)[0][-1]
            events = dict()
            events['t'] = self.timestamp[begin_index:finish_idx+1]
            events['x'] = self.xpos[begin_index:finish_idx+1]
            events['y'] = self.ypos[begin_index:finish_idx+1]
            events['p'] = self.polarity[begin_index:finish_idx+1]
            events['size'] = finish_idx - begin_index + 1
            self.delta_t_idx = finish_idx + 1
            current_time = finish_time
        return events, current_time


# 事件直方图
def event_histogram(events, height=260, width=346):
    img = np.ones((height, width, 3), dtype=np.uint8)
    # if events['size'] != 0:  # events不为空
    assert events['x'].max() < width, "out of bound events: x = {}, w = {}".format(events['x'].max(), width)
    assert events['y'].max() < height, "out of bound events: y = {}, h = {}".format(events['y'].max(), height)
    x0 = events['x'][events['p'] == 0]
    y0 = events['y'][events['p'] == 0]
    x1 = events['x'][events['p'] == 1]
    y1 = events['y'][events['p'] == 1]
    # Histogram
    for i in range(len(x0)):
        if img[y0[i], x0[i], 0] <= 2:
            img[y0[i], x0[i], 0] += 1
    for i in range(len(x1)):
        if img[y1[i], x1[i], 1] <= 2:
            img[y1[i], x1[i], 1] += 1
    img[:, :, 0] = img[:, :, 0] / 2 * 255
    img[:, :, 1] = img[:, :, 1] / 2 * 255
    img[:, :, 2] = img[:, :, 0]     # 第三个通道用第一个通道数据
    return img


# TimeSurfce
def event_timesurface(events, height=480, width=640):
    img_pos = np.full(shape=[height, width]+[1], fill_value=1, dtype=np.float64)
    img_neg = np.full(shape=[height, width]+[1], fill_value=1, dtype=np.float64)
    img_zero = np.full(shape=[height, width]+[1], fill_value=1, dtype=np.float64)   #0  #  img_pos[y_pos, x_pos, 0] = t_pos img_neg[y_neg, x_neg, 0] = t_neg
    x, y, t, p = events['x'], events['y'], events['t'], events['p']
    t_begin, t_finish = t[0], t[-1]
    t_norm = (t - t_begin) / (t_finish - t_begin)   # 归一化
    x_pos, x_neg = x[p == 1], x[p == 0]
    y_pos, y_neg = y[p == 1], y[p == 0]
    t_pos, t_neg = t_norm[p == 1], t_norm[p == 0]

    img_pos[y_neg, x_neg, 0] = 200/255
    img_neg[y_neg, x_neg, 0] = 36/255
    img_zero[y_neg, x_neg, 0] = 35/255
    #
    img_pos[y_pos, x_pos, 0] = 40 / 255
    img_neg[y_pos, x_pos, 0] = 120 / 255
    img_zero[y_pos, x_pos, 0] = 181 / 255

    img_timesurface = np.concatenate([img_pos, img_neg, img_zero], axis=-1)*255
    return img_timesurface






