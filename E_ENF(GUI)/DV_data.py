import numpy as np
import os
from tqdm import tqdm

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
        h, w = 480, 640
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


    def load_t(self, delta_t):
        # if delta_t < 1:
        #     raise ValueError("load_delta_t(): delta_t must be at least 1 micro-second: {}".format(delta_t))

        current_time = self.timestamp[self.delta_t_idx]     # 当前的时间戳
        if self.done or current_time + delta_t > self.final_time:
            self.done = True
            return np.empty((0,), dtype=np.uint32)

        finish_time = current_time + delta_t
        finish_idx = np.where(self.timestamp <= finish_time)[0][-1]
        sampling_time_finish = self.timestamp[finish_idx]
        sampling_begin_time_index = finish_idx
        while True:
            if(self.timestamp[sampling_begin_time_index]==sampling_time_finish):
                sampling_begin_time_index = sampling_begin_time_index -1
            else:
                break
        # print(self.delta_t_idx, finish_idx)
        events = dict()
        events['t'] = self.timestamp[sampling_begin_time_index+1:finish_idx+1]
        events['x'] = self.xpos[sampling_begin_time_index+1:finish_idx+1]
        events['y'] = self.ypos[sampling_begin_time_index+1:finish_idx+1]
        events['p'] = self.polarity[sampling_begin_time_index+1:finish_idx+1]
        self.delta_t_idx = finish_idx + 1
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



######## events_files#########
def event_files_sampling(source_path, fps):
    data = []
    path = source_path
    path_list = os.listdir(path)
    path_list.sort(key=lambda x: int(x[6:-4]))
    j = 0
    for i in path_list:
        fliename = path + '/' + i
        events_loader = Event_txt_loader(fliename)
        if j == 0:
            current_time = events_loader.begin_time  #####  select first current_time
            j = 1
        while True:
            events, current_time = events_loader.files_load_t(1/fps, current_time)
            polarity = []
            if events_loader.done:
                break
            x, y, t, p = events['x'], events['y'], events['t'], events['p']
            # ########取众数作为时刻极性########
            # data.append(np.argmax(np.bincount(p)))
            try:
                data.append(np.argmax(np.bincount(p)))
            except Exception:
                data.append(data[-1])
    return data


######## events_files#########
def event_files_delta_sampling(source_path, fps):
    data = []
    path = source_path
    path_list = os.listdir(path)
    path_list.sort(key=lambda x: int(x[6:-4]))
    j = 0
    for i in tqdm(path_list):
        fliename = path + '/' + i
        events_loader = Event_txt_loader(fliename)
        if j == 0:
            current_time = events_loader.begin_time  #####  select first current_time
            event_fromal = dict()
            j = 1
        while True:
            if j == 1 and current_time < events_loader.begin_time:
                polarity = event_fromal['p'].astype(np.int64)
            else:
                polarity = np.array([]).astype(np.int64)
            events, current_time = events_loader.files_load_delta_t(1/fps, current_time)
            # polarity = []
            if events_loader.done:
                event_fromal = events
                break
            x, y, t, p = events['x'], events['y'], events['t'], events['p']
            # ########取众数作为时刻极性########
            polar = np.hstack((polarity , p))
            # if(polar==[]):
            #     polar=data[-1]
            try:
                data.append(np.argmax(np.bincount(polar)))
            except Exception:
                data.append(data[-1])
    return data
