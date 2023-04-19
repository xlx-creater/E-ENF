import numpy as np
import cv2
import os
from read_txt import Event_txt_loader, event_timesurface
from tqdm import tqdm



# the event data is converted into a timesurface set
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
            if events_loader.done:
                event_fromal = events
                break
            if event_fromal:
                combined_keys = event_fromal.keys() | events.keys()
                combined_keys.remove('size')
                events = {key: np.hstack((event_fromal[key],events[key])) for key in combined_keys}
            img = event_timesurface(events, img_height, img_width)
            cv2.imwrite(event2ts_save_path + '/%06d.png' % n, img)
            n += 1
        cv2.destroyAllWindows()
    print('To Timesurfaces Done')