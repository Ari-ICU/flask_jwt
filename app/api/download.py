from flask import request, send_file
from flask_restx import Namespace, Resource
import yt_dlp
import os
import zipfile
import tempfile

download_ns = Namespace("video", description="Video operations")

DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def create_zip_from_files(zip_path, file_paths):
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file_path in file_paths:
            if os.path.exists(file_path):
                zipf.write(file_path, arcname=os.path.basename(file_path))


@download_ns.route('/download-video')
class DownloadSingleVideo(Resource):
    def get(self):
        url = request.args.get("url")
        if not url:
            return {"error": "Missing URL"}, 400

        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,  # Only single video
            'ignoreerrors': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_path = ydl.prepare_filename(info)
                return send_file(
                    video_path,
                    as_attachment=True,
                    download_name=os.path.basename(video_path)
                )
        except Exception as e:
            return {"error": f"Failed to download video: {str(e)}"}, 500


@download_ns.route('/download-playlist')
class DownloadPlaylist(Resource):
    def get(self):
        url = request.args.get("url")
        if not url:
            return {"error": "Missing URL"}, 400

        with tempfile.TemporaryDirectory() as temp_dir:
            ydl_opts = {
                'format': 'best',
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True,
                'noplaylist': False,  # Enable playlist download
            }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    entries = info.get('entries')

                    if not entries:
                        return {"error": "URL does not contain a playlist"}, 400

                    file_paths = []
                    for entry in entries:
                        if entry is None:
                            continue
                        filename = ydl.prepare_filename(entry)
                        file_paths.append(filename)

                    zip_name = f"{info.get('title', 'playlist')}.zip"
                    zip_path = os.path.join(DOWNLOAD_FOLDER, zip_name)
                    create_zip_from_files(zip_path, file_paths)

                    return send_file(
                        zip_path,
                        as_attachment=True,
                        download_name=zip_name,
                        mimetype='application/zip'
                    )
            except Exception as e:
                return {"error": f"Failed to download playlist: {str(e)}"}, 500


@download_ns.route('/download-channel')
class DownloadChannel(Resource):
    def get(self):
        url = request.args.get("url")
        if not url:
            return {"error": "Missing URL"}, 400

        with tempfile.TemporaryDirectory() as temp_dir:
            ydl_opts = {
                'format': 'best',
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True,
                'noplaylist': False,  # Must allow multiple downloads
                # 'playliststart': 1, # Optionally limit downloads
            }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    entries = info.get('entries')

                    if not entries:
                        return {"error": "URL does not contain channel videos"}, 400

                    file_paths = []
                    for entry in entries:
                        if entry is None:
                            continue
                        filename = ydl.prepare_filename(entry)
                        file_paths.append(filename)

                    zip_name = f"{info.get('title', 'channel')}.zip"
                    zip_path = os.path.join(DOWNLOAD_FOLDER, zip_name)
                    create_zip_from_files(zip_path, file_paths)

                    return send_file(
                        zip_path,
                        as_attachment=True,
                        download_name=zip_name,
                        mimetype='application/zip'
                    )
            except Exception as e:
                return {"error": f"Failed to download channel videos: {str(e)}"}, 500
