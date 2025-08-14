from flask import Flask, send_from_directory, request, jsonify
import yt_dlp
import os
from pathlib import Path

app = Flask(__name__, static_folder='static', static_url_path='/static')

# Папка для сохранения видео
DOWNLOAD_DIR = Path('видео')
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Если нужен отдельный маршрут для главной страницы
@app.route('/')
def index():
    return app.send_static_file('index.html')

# Скачивание видео по ссылке
@app.route('/api/download', methods=['POST'])
def api_download():
    data = request.get_json(silent=True) or {}
    url = data.get('url', '').strip()
    use_cookies = bool(data.get('useCookies'))

    if not url:
        return jsonify({"ok": False, "error": "Пустая ссылка"}), 400

    # Опции yt-dlp
    ydl_opts = {
        'outtmpl': str(DOWNLOAD_DIR / '%(title)s.%(ext)s'),
        'format': 'mp4/bestvideo+bestaudio/best',
        'noplaylist': True,
        'quiet': True,
    }

    cookies_path = Path('cookies.txt')
    if use_cookies and cookies_path.is_file():
        ydl_opts['cookies'] = str(cookies_path)

    # Хук для получения финального имени файла
    final_filename = { 'path': None }
    def hook(d):
        if d.get('status') == 'finished':
            p = d.get('filename')
            if p:
                final_filename['path'] = p

    ydl_opts['progress_hooks'] = [hook]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

    if not final_filename['path']:
        # fallback: пробуем найти последний файл в папке
        try:
            latest = max(DOWNLOAD_DIR.glob('*'), key=os.path.getmtime)
            final_filename['path'] = str(latest)
        except ValueError:
            return jsonify({"ok": False, "error": "Не удалось определить имя файла"}), 500

    # Возвращаем ссылку на скачанный файл
    abs_path = Path(final_filename['path']).resolve()
    if DOWNLOAD_DIR.resolve() not in abs_path.parents and abs_path != DOWNLOAD_DIR.resolve():
        return jsonify({"ok": False, "error": "Неверный путь файла"}), 500

    return jsonify({
        "ok": True,
        "filename": abs_path.name,
        "downloadUrl": f"/downloads/{abs_path.name}"
    })

# Раздача загруженных файлов
@app.route('/downloads/<path:filename>')
def downloads(filename):
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))  # Render назначает свой порт
    app.run(host='0.0.0.0', port=port, debug=True)
