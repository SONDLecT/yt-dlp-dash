# Quick Start Guide - yt-dlp Web

## 🚀 Get Started in 3 Steps

### Step 1: Build and Run
```bash
cd ytdlp-web
docker-compose up -d
```

### Step 2: Access the Interface
Open your browser and go to:
```
http://localhost:5000
```

### Step 3: Download Your First Video
1. Paste a YouTube URL
2. Choose your quality settings
3. Click "Download"

That's it! Your video will download and appear in the "Downloaded Files" section.

## 📁 Where are my files?

Files are saved to the `downloads/` directory in the same folder as your docker-compose.yml file.

## 🎯 Common Use Cases

### Download a YouTube Video
```
URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ
Quality: Best Quality
→ Click Download
```

### Download Audio Only (MP3)
```
URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ
☑ Audio Only (MP3)
→ Click Download
```

### Download a Playlist
```
URL: https://www.youtube.com/playlist?list=PLxxxxxxxxx
Quality: 720p
→ Click Download (downloads all videos)
```

### Download Specific Videos from a Playlist
```
URL: https://www.youtube.com/playlist?list=PLxxxxxxxxx
⚙️ Advanced Options
  Playlist Start: 5
  Playlist End: 10
→ Click Download (downloads videos 5-10)
```

### Download with Subtitles
```
URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ
☑ Download Subtitles
→ Click Download
```

## 🔧 Advanced Features

### Custom Output Template
Want to organize files by uploader?
```
⚙️ Advanced Options
Output Template: %(uploader)s/%(title)s.%(ext)s
```

### Custom yt-dlp Flags
Need more control? Use JSON flags:
```json
{
  "writeinfojson": true,
  "writethumbnail": true,
  "embedthumbnail": true,
  "format": "bestvideo[height<=1080]+bestaudio/best"
}
```

## 🛠️ Customization

### Change Port
Edit `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"  # Now access at http://localhost:8080
```

### Change Download Directory
Edit `docker-compose.yml`:
```yaml
volumes:
  - /path/to/your/media:/downloads
```

## 📱 Works With

- YouTube (videos, playlists, channels)
- Vimeo
- Twitter/X
- TikTok
- Twitch
- Reddit
- Instagram
- Facebook
- And 1000+ more sites!

## 🐛 Troubleshooting

### Container won't start
```bash
docker-compose logs
```

### Downloads not appearing
Check the downloads folder was created and is writable:
```bash
ls -la downloads/
```

### Update yt-dlp
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 💡 Tips

- Use the "Best Quality" option for maximum quality
- Check "Audio Only" for music videos to save space
- Use playlist start/end to grab specific episodes from a series
- The download progress shows real-time speed and ETA
- Files persist in your downloads folder even if the container restarts

## 🔒 Security

- This is designed for local/private network use
- Don't expose port 5000 to the internet without authentication
- Always respect copyright and terms of service

---

Need more help? Check the full README.md for detailed documentation!
