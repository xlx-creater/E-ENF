import numpy as np
import cv2
import os
from read_txt import Event_txt_loader, event_histogram, event_timesurface
from tqdm import tqdm

# 将事件数据转换为视频
def event2video(soarce_path, save_path, show=True, save=True):
    events_loader = Event_txt_loader(soarce_path)
    img_height = 260
    img_width = 346
    fps = 30
    video_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'XVID'), fps, (img_width, img_height))
    # if show:
    #     cv2.namedWindow('out', cv2.WINDOW_NORMAL)
    while True:
        events = events_loader.load_delta_t(1/fps)
        if events_loader.done:
            break
        vis = event_histogram(events, img_height, img_width)
        # if show:
        #     cv2.imshow('out', vis)
        if save:
            video_writer.write(np.int8(vis))
        cv2.waitKey(1)
    video_writer.release()
    cv2.destroyAllWindows()


# 将事件数据转换为图片（histogram）集
def event2imgs(soarce_path, save_path, fps=30):
    events_loader = Event_txt_loader(soarce_path)
    img_height = 480
    img_width = 640
    n = 0
    # fps = 30
    while True:
        events = events_loader.load_delta_t(1/fps)
        if events_loader.done:
            break
        img = event_histogram(events, img_height, img_width)
        cv2.imwrite(save_path + '/%06d.png' % n, img)
        n += 1
    cv2.destroyAllWindows()


# 将事件数据转换为图片（histogram）集
def events2imgs(source_path, save_path, fps=30):
    path = source_path
    path_list = os.listdir(path)
    path_list.sort(key=lambda x: int(x[6:-4]))
    j = 0
    img_height = 480
    img_width = 640
    n = 0
    events_finish = dict()
    for i in path_list:
        fliename = path + '/' + i
        events_loader = Event_txt_loader(fliename)
        if j == 0:
            current_time = events_loader.begin_time  #####  select first current_time
            j = 1
        while True:
            events, current_time, events_finish = events_loader.files_load_delta_t(1 / fps, current_time, events_finish)
            if events_loader.done:
                break
            # x, y, t, p = events['x'], events['y'], events['t'], events['p']
            img = event_histogram(events, img_height, img_width)
            cv2.imwrite(save_path + '/%06d.png' % n, img)
            n += 1
            # if n==1800:     #只保留一分钟的
            #     break
        cv2.destroyAllWindows()

# 将事件数据转换为图片（histogram）集
def event2timesurfaces(soarce_path, save_path, fps=30):
    events_loader = Event_txt_loader(soarce_path)
    img_height = 480
    img_width = 640
    n = 0
    fps = fps
    while True:
        events = events_loader.load_delta_t(1/fps)
        if events_loader.done:
            break
        img = event_timesurface(events, img_height, img_width)
        cv2.imwrite(save_path + '/%06d.png' % n, img)
        n += 1
    cv2.destroyAllWindows()



# 将事件数据转换为timesurface集
def events2timesurfaces(source_path, fps=30):
    path = source_path + '/events'
    path_list = os.listdir(path)
    path_list.sort(key=lambda x: int(x[6:-4]))
    events_finish = dict()
    j = 0
    img_height = 480
    img_width = 640
    n = 0
    for i in tqdm(path_list):
        fliename = path + '/' + i
        event2ts_save_path = source_path + '/event2ts'
        if not os.path.exists(event2ts_save_path):
            os.mkdir(event2ts_save_path)
        events_loader = Event_txt_loader(fliename)
        if j == 0:
            current_time = events_loader.begin_time  #####  select first current_time
            event_fromal = dict()
            j = 1
        while True:
            if j == 1 and current_time < events_loader.begin_time:
                event_fromal = event_fromal
            else:
                event_fromal = dict()
            events, current_time = events_loader.files_load_delta_t(1 / fps, current_time)
            # polarity = []
            if events_loader.done:
                event_fromal = events
                break
            if event_fromal:
                combined_keys = event_fromal.keys() | events.keys()
                combined_keys.remove('size')
                events = {key: np.hstack((event_fromal[key],events[key])) for key in combined_keys}

            # x, y, t, p = events['x'], events['y'], events['t'], events['p']
            img = event_timesurface(events, img_height, img_width)
            cv2.imwrite(event2ts_save_path + '/%06d.png' % n, img)
            n += 1
        cv2.destroyAllWindows()
    print('To Timesurfaces Done')