# yt-dlp-dash

A self-hosted web interface for [yt-dlp](https://github.com/yt-dlp/yt-dlp).

Download videos from YouTube and [1000+ other sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md) through a clean, browser-based UI—no command line required.

<p align="center">
  <img src="yt-dlp-screen-light.png" alt="Light theme" width="45%">
  <img src="yt-dlp-dash-screen-dark.png" alt="Dark theme" width="45%">
</p>

## Features

- Download videos and playlists from YouTube and 1000+ supported sites
- Quality selection (4K, 1080p, 720p, etc.) and format options
- Audio-only extraction with MP3 conversion
- Subtitle downloads
- Real-time progress tracking
- Built-in file manager for retrieving downloads
- Custom yt-dlp flags via JSON for advanced users
- Runs in Docker with minimal configuration

## Quick Start

```bash
# Clone the repository
git clone https://github.com/SONDLecT/yt-dlp-dash.git
cd yt-dlp-dash

# Copy and configure docker-compose
cp docker-compose.example.yml docker-compose.yml

# Build and run
docker compose up --build -d
```

Open `http://localhost:5000` in your browser.

### Configuration

Edit `docker-compose.yml` to customize:

| Setting | Description |
|---------|-------------|
| `5000:5000` | Change the first number to use a different port |
| `user: "1000:1000"` | Match your UID/GID (run `id -u` and `id -g`) |
| Volumes | Mount additional directories for downloads |

## Usage

**Basic download**: Paste a URL, select quality, click Download.

**Audio only**: Check "Audio Only (MP3)" to extract audio.

**Playlists**: Paste a playlist URL. Use Advanced Options to set start/end indices.

**Advanced Options**: Access custom output templates, playlist ranges, and arbitrary yt-dlp flags via JSON:

```json
{
  "writeinfojson": true,
  "writethumbnail": true,
  "embedthumbnail": true,
  "format": "bestvideo[height<=1080]+bestaudio/best"
}
```

## Updating

```bash
git pull
docker compose up --build -d
```

To force a fresh yt-dlp version:

```bash
docker compose build --no-cache
docker compose up -d
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Format not available" | Try "Best Quality" or a different preset |
| Audio extraction fails | Check logs: `docker logs ytdlp-web` |
| Can't access UI | Verify port isn't in use, check firewall, confirm container is running (`docker ps`) |

## Security

This application is designed for private network use. If exposing to the internet:

- Add authentication (reverse proxy with basic auth, Authelia, etc.)
- Use HTTPS
- Restrict access by IP if possible

Respect copyright laws and terms of service when downloading content.

## Tech Stack

- **Backend**: Flask (Python 3.11)
- **Downloader**: yt-dlp
- **Media processing**: ffmpeg
- **Container**: Docker

## License

This project is released into the public domain under the [Unlicense](https://unlicense.org/). See [LICENSE](LICENSE) for details.

## Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for the excellent download engine
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [ffmpeg](https://ffmpeg.org/) for media processing
