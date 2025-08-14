
import yt_dlp
import os

os.makedirs("видео", exist_ok=True)

url = input("Вставь ссылку на Instagram (или другую платформу): ")

ydl_opts = {

    'outtmpl': 'видео/%(title)s.%(ext)s',
    'format': 'mp4/bestvideo+bestaudio/best',
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])

print("✅ Видео скачано в папку 'видео'")
