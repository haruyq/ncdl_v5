import os
import subprocess

class Extension:
    @staticmethod
    def clear_screen():
        if os.name == 'posix':
            _ = os.system('clear')
        else:
            _ = os.system('cls')

    @staticmethod
    def convert(input_file, output_file, codec=None, bitrate=None, extra_args=None):
        """
        FFmpegを使って音声ファイルを変換する関数

        :param input_file: 入力ファイルのパス
        :param output_file: 出力ファイルのパス
        :param codec: 使用するコーデック（例: 'mp3', 'aac'）
        :param bitrate: ビットレート（例: '192k'）
        :param extra_args: FFmpegに渡す追加の引数（リスト）
        """
        ffmpeg_path = os.path.join('FFmpeg', 'bin', 'ffmpeg')
        if os.name == 'nt':
            ffmpeg_path += '.exe'

        codec_map = {
            'ogg': 'libvorbis',
        }
        if codec in codec_map:
            codec_to_use = codec_map[codec]
        else:
            codec_to_use = codec

        cmd = [ffmpeg_path, '-y', '-i', input_file]

        if codec_to_use:
            cmd += ['-acodec', codec_to_use]

        if bitrate:
            cmd += ['-b:a', bitrate]

        if extra_args:
            cmd += extra_args

        cmd.append(output_file)

        subprocess.run(cmd, check=True)