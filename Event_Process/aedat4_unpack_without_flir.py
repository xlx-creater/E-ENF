# 解包.aedat4文件，仅包括davis
from dv import AedatFile
import os
import numpy as np
from event_visualize import events2timesurfaces
from os.path import dirname, abspath

# 解包一个文件夹下的所有文件
def unpack(data_path: object, save_path: object, if_visualize: object = True) -> object:
    os.chdir(data_path)
    aedatfiles = os.listdir()
    for filename in aedatfiles:
        os.chdir(data_path)
        # 1. 解包文件
        unpack_events_file(filename, save_path)
        # 2. time_surface
        file_name = os.path.basename(filename).split('.')[0]
        files = save_path + '/' + file_name
        # if not os.path.exists(save_path + '/' + file_name + '/time_surface'):
        #     os.mkdir(save_path + '/' + file_name + '/time_surface')
        # time_surface_path = save_path + '/' + file_name + '/time_surface'
        events2timesurfaces(files, fps = 30)

    print('All Done')



def unpack_events_file(file_path, save_path):
    file_name = os.path.basename(file_path).split('.')[0]
    print(file_name)
    if not os.path.exists(save_path + '/' + file_name):
        os.mkdir(save_path +  '/' + file_name)
    if not os.path.exists(save_path + '/' + file_name + '/events'):
        os.mkdir(save_path + '/' + file_name + '/events')
    i = 0
    with AedatFile(file_path) as f:
        for e in f['events'].numpy():
            # print(e.shape)
        # events = np.hstack([packet for packet in f['events'].numpy()])
            events = np.array([e['timestamp'] / 1e6, e['x'], e['y'], e['polarity']]).T
        # 写入event数据
            event_file = open(save_path + '/' + file_name + '/events' + '/events{}.txt'.format(i), 'w+')
            for j in range(len(events)):
                event_file.write('%f %d %d %d\n' % (events[j, 0], events[j, 1], events[j, 2], events[j, 3]))
            event_file.close()
            i = i +1
    print('To Events Done')




if __name__ == '__main__':
    path = dirname(dirname(abspath(__file__)))
    data_path = path + '/Events/Raw'
    save_path = path + '/Events/Unpacked'
    unpack(data_path, save_path)









