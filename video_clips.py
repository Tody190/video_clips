#coding=UTF-8
_author_ = 'yangtao'
__version__ = '1.03'

dezerling_show = " _______   _______  ________   _______ .______       __       __  .__   __. \n"
dezerling_show += "|       \ |   ____||       /  |   ____||   _  \     |  |     |  | |  \ |  | \n"
dezerling_show += "|  .--.  ||  |__   `---/  /   |  |__   |  |_)  |    |  |     |  | |   \|  | \n"
dezerling_show += "|  |  |  ||   __|     /  /    |   __|  |      /     |  |     |  | |  . `  | \n"
dezerling_show += "|  '--'  ||  |____   /  /----.|  |____ |  |\  \----.|  `----.|  | |  |\   | \n"
dezerling_show += "|_______/ |_______| /________||_______|| _| `._____||_______||__| |__| \__|"
print(dezerling_show)
import getpass

user_name = getpass.getuser()
if user_name:
    print("Welcome! %s" % user_name)
print('')


import os

import edl
from video import Editor
import config




def check(edl_file, video_file, out_path):
    check_result = True
    if not os.path.isfile(edl_file):
        print("\n%s EDL不存在"%edl_file)
        check_result = False
    if not os.path.isfile(video_file):
        print("\n%s 视频不存在"%video_file)
        check_result = False
    if not os.path.isdir(out_path):
        print("\n%s 输出路径不存在" % out_path)
    return check_result


def main(edl_file, video_file, out_path):
    if not check(edl_file, video_file, out_path):
        return

    video_editor = Editor(video_file)
    # 获取视频帧速率
    fps = video_editor.fps
    #读取EDL信息（名字和帧数范围）
    edlconfig = config.read()['EDL']
    track = edlconfig['track']
    print("Read track: ", track)
    video_edl_info = edl.Reader(fps, edl_file, track=track)
    # 计算每个视频片段的开始结束时间
    hander_frame = None
    for video_info in video_edl_info:
        clip_name = video_info.clip_name
        if clip_name:
            # 去后缀
            clip_name = os.path.splitext(clip_name)[0]
            if not hander_frame:
                hander_frame = int(video_info.timecode_in.frames)
            clip_start_frame = video_info.timecode_in.frames - hander_frame + 1
            clip_end_frame = video_info.timecode_out.frames - hander_frame
            cutting = video_editor.cutting_frame(out_path, clip_name)
            print("--------------------------")
            print("Clip Name: ", clip_name)
            print("Frame Range:", clip_start_frame, "-", clip_end_frame)
            print("Timecode:", video_info.timecode_in)
            cutting.run(clip_start_frame, clip_end_frame, timecode=video_info.timecode_in)
    print("\nDone!")




if __name__ == "__main__":
    # edl_file = r"M:\temp\video\changde.edl"
    # filename = r"M:\temp\video\changde.mov"
    # out_path = r"M:\temp\video\output_mov"
    # main(edl_file, filename, out_path)
    import tkinter as tk

    uiconfig = config.read()['UI']

    root = tk.Tk()
    root.title('DeZerlin Video Clips %s by yangtao'%__version__)
    root.geometry('500x100')
    root.iconbitmap(config.window_icon)
    # EDL 框架
    EDL_frame = tk.Frame(root)
    EDL_frame.pack(side=tk.TOP, fill=tk.X, expand=tk.YES)
    # EDL 便签
    EDL_label = tk.Label(EDL_frame, text="EDL")
    EDL_label.pack(side=tk.LEFT)
    # EDL 输入框
    edl_config_var = tk.StringVar()
    edl_config_var.set(uiconfig['edl'])
    EDL_entry = tk.Entry(EDL_frame, textvariable=edl_config_var)
    EDL_entry.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)

    # video 框架
    video_frame = tk.Frame(root)
    video_frame.pack(side=tk.TOP, fill=tk.X, expand=tk.YES)
    # 视频标签
    video_label = tk.Label(video_frame, text="视频")
    video_label.pack(side=tk.LEFT)
    # 视频输入
    video_config_var = tk.StringVar()
    video_config_var.set(uiconfig['video'])
    video_entry = tk.Entry(video_frame, textvariable=video_config_var)
    video_entry.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)

    # 保存路径框架
    out_frame = tk.Frame(root)
    out_frame.pack(side=tk.TOP, fill=tk.X, expand=tk.YES)
    # 保存路径标签
    out_label = tk.Label(out_frame, text="输出路径")
    out_label.pack(side=tk.LEFT)
    # 保存路径输入
    out_config_var = tk.StringVar()
    out_config_var.set(uiconfig['out'])
    out_entry = tk.Entry(out_frame, textvariable=out_config_var)
    out_entry.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)


    def run():
        EDL_entry_var = EDL_entry.get()
        video_entry_var = video_entry.get()
        out_entry_var = out_entry.get()

        # 写入配置文件
        config.write('UI',
                     edl=EDL_entry_var,
                     video=video_entry_var,
                     out=out_entry_var)

        main(EDL_entry_var, video_entry_var, out_entry_var)

    # 开始按钮
    start_button = tk.Button(root, text='开始', command=run)
    start_button.pack(fill=tk.X, anchor=tk.S, expand=tk.YES)

    root.mainloop()