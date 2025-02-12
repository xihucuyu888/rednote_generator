import os
import yt_dlp
import subprocess
import whisper
import requests  # 导入 requests 模块

# 初始化 Whisper 模型
model = whisper.load_model("base")

def extract_video_url_from_xiaohongshu(url):
    """
    使用 yt-dlp 从小红书 URL 中提取视频地址
    """
    ydl_opts = {
        'format': '0',  # 选择格式 ID 0，即 720p
        'quiet': True,  # 禁止输出日志
        'extractaudio': True,  # 提取音频
        'outtmpl': 'temp_note/%(id)s.%(ext)s',  # 指定下载目录为 temp_note 文件夹，并且使用视频的 ID 作为文件名
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_url = info_dict.get('url', None)
            title = info_dict.get('title', 'unknown_video')
            return video_url, title
    except yt_dlp.utils.ExtractorError as e:
        print(f"视频提取错误: {e}")
        return None, None

def generate_unique_filename(title, extension):
    """
    根据视频标题生成唯一文件名，防止非法字符和重复
    """
    # 使用标题生成文件名，替换掉非法字符
    safe_title = "".join(c if c.isalnum() or c in ('-', '_', '.') else '_' for c in title)
    return f"temp_note/{safe_title}{extension}"

def download_video(url, download_path):
    """
    从指定的 URL 下载视频文件
    """
    response = requests.get(url, stream=True)
    with open(download_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    print(f"视频下载成功，保存路径：{download_path}")

def extract_audio_from_mp4(mp4_path, audio_path):
    """
    使用 ffmpeg 提取音频
    """
    command = [
        "ffmpeg", 
        "-i", mp4_path,          # 输入 MP4 文件
        "-vn",                   # 不处理视频流
        "-acodec", "pcm_s16le",  # 音频编码格式
        "-ar", "16000",          # 音频采样率
        "-ac", "1",              # 单声道
        audio_path               # 输出音频文件
    ]
    subprocess.run(command, check=True)

def transcribe_audio(audio_path):
    """
    使用 whisper 进行音频转录
    """
    result = model.transcribe(audio_path)
    return result['text']

def process_url_file(url_file):
    """
    处理 url.txt 中的每个 URL，抓取视频、下载
    """
    with open(url_file, 'r') as file:
        urls = file.readlines()

    for url in urls:
        url = url.strip()  # 去除空白字符
        print(f"正在处理：{url}")
        
        # 从小红书 URL 提取视频 URL 和视频标题
        video_url, title = extract_video_url_from_xiaohongshu(url)
        
        if video_url:
            print(f"视频地址：{video_url}")
            # 创建 temp_note 文件夹（如果不存在）
            os.makedirs("temp_note", exist_ok=True)
            
            # 根据视频标题生成唯一的文件名
            video_path = generate_unique_filename(title, ".mp4")
            #audio_path = generate_unique_filename(title, ".wav")
            
            # 下载视频
            download_video(video_url, video_path)
            
            # # 提取音频
            # extract_audio_from_mp4(video_path, audio_path)
            
            # # 转录音频
            # transcript = transcribe_audio(audio_path)
            # print(f"转录结果：\n{transcript}\n")
            
            # # 保存转录结果
            # transcript_filename = f"transcript_{os.path.basename(video_path)}.txt"
            # with open(transcript_filename, 'w') as f:
            #     f.write(transcript)
            
            # print(f"转录结果已保存为：{transcript_filename}")

# 设置 URL 文件路径
url_file = "url.txt"

# 执行处理
process_url_file(url_file)
