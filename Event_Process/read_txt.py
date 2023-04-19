import numpy as np

class Event_txt_loader:
    def __init__(self, path):
        self.events = np.loadtxt(path)
        self.timestamp = self.events[:, 0]
        self.xpos = np.int32(self.events[:, 1])
        self.ypos = np.int32(self.events[:, 2])
        self.polarity = np.uint32(self.events[:, 3])

        self.size = len(self.timestamp)
        h, w = 260, 346
        self.shape = (h, w) # h, w

        self.begin_time = self.timestamp[0]
        self.final_time = self.timestamp[-1]
        self.delta_t_idx = 0
        self.done = False

    # 单位：秒
    def load_delta_t(self, delta_t):
        # if delta_t < 1:
        #     raise ValueError("load_delta_t(): delta_t must be at least 1 micro-second: {}".format(delta_t))

        current_time = self.timestamp[self.delta_t_idx]
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

        # current_time = self.timestamp[self.delta_t_idx]
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
        events = dict()
        events['t'] = self.timestamp[sampling_begin_time_index + 1:finish_idx + 1]
        events['x'] = self.xpos[sampling_begin_time_index + 1:finish_idx + 1]
        events['y'] = self.ypos[sampling_begin_time_index + 1:finish_idx + 1]
        events['p'] = self.polarity[sampling_begin_time_index + 1:finish_idx + 1]
        self.delta_t_idx = finish_idx + 1
        current_time = finish_time
        return events, current_time

    def files_load_delta_t(self, delta_t, current_time):

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



# TimeSurfce
def event_timesurface(events, height=480, width=640):
    img_pos = np.full(shape=[height, width]+[1], fill_value=1, dtype=np.float64)
    img_neg = np.full(shape=[height, width]+[1], fill_value=1, dtype=np.float64)
    img_zero = np.full(shape=[height, width]+[1], fill_value=1, dtype=np.float64)
    x, y, t, p = events['x'], events['y'], events['t'], events['p']
    t_begin, t_finish = t[0], t[-1]
    t_norm = (t - t_begin) / (t_finish - t_begin)
    x_pos, x_neg = x[p == 1], x[p == 0]
    y_pos, y_neg = y[p == 1], y[p == 0]
    t_pos, t_neg = t_norm[p == 1], t_norm[p == 0]

    img_pos[y_neg, x_neg, 0] = 46/255
    img_neg[y_neg, x_neg, 0] = 57/255
    img_zero[y_neg, x_neg, 0] = 242/255
    #
    img_pos[y_pos, x_pos, 0] = 242 / 255
    img_neg[y_pos, x_pos, 0] = 121 / 255
    img_zero[y_pos, x_pos, 0] = 57 / 255

    img_timesurface = np.concatenate([img_pos, img_neg, img_zero], axis=-1)*255
    return img_timesurface






