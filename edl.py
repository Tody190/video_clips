#coding=UTF-8
_author_ = 'yangtao'

from timecode import Timecode
import re
import config




cmx3600_str = config.read()['EDL']['re']
cmx3600_re = re.compile(cmx3600_str, re.M)


class item():
    def __init__(self, framerate, data):
        self.framerate = framerate
        self.num = None
        self.src_tape_name = None
        self.track = None
        self.transition = None
        self.src_in = None
        self.src_out = None
        self.timecode_in = None
        self.timecode_out = None
        self.clip_name = None

        self.__set_data(data)

    def __set_data(self, data):
        for i, item in enumerate(data):
            if i == 0:
                self.num = item
            elif i == 1:
                self.src_tape_name = item
            elif i == 2:
                self.track = item
            elif i == 3:
                self.transition = item
            elif i == 4:
                self.src_in = Timecode(self.framerate, item)
            elif i == 5:
                self.src_out = Timecode(self.framerate, item)
            elif i == 6:
                self.timecode_in = Timecode(self.framerate, item)
            elif i == 7:
                self.timecode_out = Timecode(self.framerate, item)
            else:
                if '* FROM CLIP NAME: ' in item:
                    self.clip_name = item.split('* FROM CLIP NAME: ')[-1]


class Reader(list):
    def __init__(self, frame, edl_file, **kwargs):
        self.__filter_map = kwargs
        self.framerate = frame
        self.edl_file = edl_file
        self.edl_body = self.__read(edl_file)
        self.__set_items()

    def __read(self, file):
        with open(file, 'r') as f:
            return f.read()

    def __set_items(self):
        items = cmx3600_re.findall(self.edl_body)
        print("RE: %s"%cmx3600_str)
        if items:
            for item_data in items:
                item_entity = item(self.framerate, item_data)
                if self.__filter(item_entity):
                    self.append(item_entity)

    def __filter(self, item):
        if self.__filter_map:
            for k in self.__filter_map:
                if str(item.__getattribute__(k)).lower() in str(self.__filter_map[k]).lower():
                    return item
        else:
            return item




if __name__ == '__main__':
    edl_file = r"D:\temp\test_cut_mov_with_edl\changde.edl"
    vt = Reader('24', edl_file, track="V")
    print(vt)