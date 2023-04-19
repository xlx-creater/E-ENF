from dv import AedatFile
import os
import numpy as np
from event_visualize import events2timesurfaces
from os.path import dirname, abspath


def unpack(data_path: object, save_path: object, if_visualize: object = True) -> object:
    file_type_list = ['aedat4']
    os.chdir(data_path)
    aedatfiles = os.listdir()
    for filename in aedatfiles:
        file_type = filename.split('.')[-1]
        if (file_type in file_type_list):
            os.chdir(data_path)
            # 1. unpacking files
            unpack_events_file(filename, save_path)
            # 2. time_surface
            file_name = os.path.basename(filename).split('.')[0]
            files = save_path + '/' + file_name
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
            events = np.array([e['timestamp'] / 1e6, e['x'], e['y'], e['polarity']]).T
        # write event data
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









