#coding=UTF-8
_author_ = 'yangtao'


import os
import subprocess
import json
import tempfile




ffprobe = os.path.dirname(__file__).replace('\\', '/') + '/ffmpeg/ffprobe.exe'
ffpmpeg = os.path.dirname(__file__).replace('\\', '/') + '/ffmpeg/ffmpeg.exe'
print("ffpmpeg: ", ffpmpeg)
print("ffprobe: ", ffprobe)


class Cutting():
    FILE = None
    FPS = None
    DURATION_FRAMES = None
    CODEC = None
    PIX_FMT = None
    def __init__(self, out_path: str, video_name: 'name.ext'):
        self.out_path = out_path
        self.video_name = video_name

    def __get_cutting_point(self, start_frame: int, end_frame: int):
        start_index = "None"
        end_index = "None"
        for i, point_frame in enumerate(self.__frame_points):
            if start_index == "None":
                if start_frame == point_frame:
                    start_index = i
                elif start_frame < point_frame:
                    start_index = i-1
            if end_index == "None":
                if end_frame == point_frame:
                    end_index = i
                elif end_frame < point_frame:
                    end_index = i
        if not start_index:
            start_index = 0
        if not end_index:
            end_index = len(self.__second_points) - 1
        return start_index, end_index

    def frame_to_mov(self, in_frames, timecode):
        out_file = '{0}/{1}'.format(self.out_path, "%s.mov"%self.video_name)
        cmd = [ffpmpeg, '-r', str(self.FPS), '-i', in_frames,
               '-pix_fmt', self.PIX_FMT, '-vcodec', self.CODEC, '-preset', 'slow',
               '-timecode', str(timecode),
               '-y', out_file]
        #print(cmd)
        p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        #print(out)
        #print(err)

    def cutting_with_frame(self, start_frame, end_frame, temp_path):
        # 定位剪切的开始/结束时间
        start_point_second, residue = divmod(start_frame, self.FPS)
        if residue == 0:
            # 当没有余数的时候，应该为上秒的尾数帧，应该 -1s
            start_point_second -= 1
        end_point_second, residue = divmod(end_frame, self.FPS)
        if residue != 0:
            # 当有余数的时候应该 +1s
            end_point_second += 1

        # 定位剪切开始结束帧数
        start_point_frame = start_point_second*self.FPS + 1
        end_point_frame = end_point_second*self.FPS

        #print("时间剪切点:", (start_point_second, end_point_second))
        #print("帧数剪切点:", (start_point_frame, end_point_frame))

        # 剪切
        out_file = '{0}/{1}'.format(temp_path, 'point_temp_%08d.dpx')
        cmd = [ffpmpeg, '-r', str(self.FPS), '-ss', '%s'%start_point_second, '-to', '%s'%end_point_second,
               '-accurate_seek', '-i', self.FILE, '-r', str(self.FPS), out_file]
        #print(cmd)
        p = subprocess.Popen(cmd,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()

        # 获取所有导出序列
        seq = []
        for file_name in os.listdir(temp_path):
            seq.append(os.path.join(temp_path, file_name))
        seq.sort()
        #print("剪切总帧", len(seq))

        # 通过序列数量判断帧长，如果实际帧数长度小于预计长度，使用实际长度做尾帧
        seq_duration = len(seq)
        if end_point_frame - start_point_frame + 1 > seq_duration:
            end_point_frame = seq_duration

        # 计算实际需要使用的序列
        del_head_num = start_frame - start_point_frame
        if del_head_num == 0:
            del_head_num = None
        del_tail_num = end_frame - end_point_frame
        if del_tail_num == 0:
            del_tail_num = None
        seq = seq[del_head_num:del_tail_num]
        #print("实际使用帧数", len(seq))

        # 重命名序列
        for i, filename in enumerate(seq):
            new_filename = os.path.join(temp_path, 'temp_%s.dpx'%str(i))
            newname = os.path.join(filename, new_filename)
            os.rename(filename, newname)

        # 将重命名的序列合成视频
        in_frames = "{0}/{1}".format(temp_path, 'temp_%d.dpx')
        self.frame_to_mov(in_frames, self.timecode)

        # 删除所有帧数
        seq = os.listdir(temp_path)
        for s in seq:
            file_path = os.path.join(temp_path, s)
            try:
                os.remove(file_path)
            except:
                pass

    def __sort_out_frame(self, seq, start_frame, end_frame):
        frame_duration = end_frame - start_frame + 1
        del_files = seq[frame_duration:]
        for f in del_files:
            os.remove(f)

    def run(self, start_frame: int, end_frame: int, timecode: str):
        if end_frame <= start_frame:
            return
        self.timecode = timecode
        with tempfile.TemporaryDirectory() as tmpdirname:
            # 剪切成序列
            self.cutting_with_frame(start_frame, end_frame, tmpdirname)


class Editor():
    def __init__(self, file):
        self.file = file
        self.__video_info = self.__video_info()
        self.fps = self.__fps()
        self.codec = self.__codec()
        self.pix_fmt = self.__pix_fmt()
        self.duration_frames = self.__duration_frames()
        self.__tmp_dir = tempfile.gettempdir()

        # 设置 cutting 类
        Cutting.FILE = self.file
        Cutting.FPS = self.fps
        Cutting.DURATION_FRAMES = self.duration_frames
        Cutting.CODEC = self.codec
        Cutting.PIX_FMT = self.pix_fmt

    def __video_info(self):
        cmd = [ffprobe, '-show_streams', '-of', 'json', self.file]
        #print(cmd)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        out_json = json.loads(out.decode('utf-8'))
        #pprint.pprint(out_json)
        return out_json

    def __analyisi_info(self, video_info, key):
        if isinstance(video_info, dict):
            if key in video_info:
                return video_info[key]
            else:
                return self.__analyisi_info(list(video_info.values()), key)
        if isinstance(video_info, list):
            for v in video_info:
                result = self.__analyisi_info(v, key)
                if result:
                    return result

    def __fps(self):
        # 获取 streams 里 r_frame_rate 的值
        r_frame_rate = self.__analyisi_info(self.__video_info, "r_frame_rate")
        # 将 r_frame_rate 转为帧速率
        if '/' in r_frame_rate:
            Numerator = r_frame_rate.split("/")[0]
            denominator = r_frame_rate.split("/")[-1]
            fps = int(Numerator) / int(denominator)
            return int(fps)
        else:
            return int(r_frame_rate)

    def __duration_frames(self):
        # 获取总帧长
        return self.__analyisi_info(self.__video_info, 'duration_ts')

    def __codec(self):
        # 获取编码名
        return self.__analyisi_info(self.__video_info, 'codec_name')

    def __pix_fmt(self):
        # 获取色彩空间
        return self.__analyisi_info(self.__video_info, 'pix_fmt')

    def cutting_frame(self, out_path, video_name):
        cutting = Cutting(out_path, video_name)
        return cutting




if __name__ == "__main__":
    filename = r"D:\temp\test_cut_mov_with_edl\changde.mov"