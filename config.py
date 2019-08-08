#coding=UTF-8
_author_ = 'yangtao'


import os
import configparser
import collections




window_icon = os.path.dirname(__file__).replace('\\', '/') + '/videoclips.ico'
config_path = os.path.dirname(__file__).replace('\\', '/') + '/config.ini'
print("config path:", config_path)


def read():
    config = configparser.ConfigParser()
    config.read(config_path)
    return config


def write(section, **kwargs):
    config = read()
    config_dict = collections.OrderedDict()
    for sect in config.sections():
        section_dict = collections.OrderedDict()
        for k in config[sect]:
            section_dict[k] = config[sect][k]
        config_dict[sect] = section_dict

    for k in kwargs:
        if not section in config:
            config[section] = collections.OrderedDict()
        config[section][k] = kwargs[k]

    with open(config_path, 'w') as configfile:
        config.write(configfile)




if __name__ == "__main__":
    write("UI", edl = r"M:\temp\video\changde.edl")

