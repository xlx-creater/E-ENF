import numpy as np
import os

class Event_txt_loader:
    def __init__(self, path):
        self.events = np.loadtxt(path)
        self.timestamp = self.events[:, 0]
        self.xpos = np.int32(self.events[:, 1])
        self.ypos = np.int32(self.events[:, 2])
        self.polarity = np.uint32(self.events[:, 3])

        self.size = len(self.timestamp)
        h, w = 480, 640
        self.shape = (h, w) # h, w

        self.begin_time = self.timestamp[0]
        self.final_time = self.timestamp[-1]
        self.delta_t_idx = 0
        self.done = False

    def load_delta_t(self, delta_t):

        current_time = self.timestamp[self.delta_t_idx]     # the current timestamp
        if self.done or current_time + delta_t > self.final_time:
            self.done = True
            return np.empty((0,), dtype=np.uint32)

        finish_time = current_time + delta_t
        finish_idx = np.where(self.timestamp < finish_time)[0][-1]

        events = dict()
        events['t'] = self.timestamp[self.delta_t_idx:finish_idx+1]
        events['x'] = self.xpos[self.delta_t_idx:finish_idx+1]
        events['y'] = self.ypos[self.delta_t_idx:finish_idx+1]
        events['p'] = self.polarity[self.delta_t_idx:finish_idx+1]
        events['size'] = finish_idx - self.delta_t_idx + 1
        self.delta_t_idx = finish_idx + 1
        return events

    # For a given timestamp, read the events from the previous time
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
            try:
                data.append(np.argmax(np.bincount(p)))
            except Exception:
                data.append(data[-1])
    return data

