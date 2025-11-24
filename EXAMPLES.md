# yt-dlp Web - Examples & Use Cases

## Video Quality Examples

### Maximum Quality (4K if available)
```
Format: Best Quality
Custom Flags: 
{
  "format": "bestvideo[height<=2160]+bestaudio/best"
}
```

### 1080p with Best Audio
```
Format: 1080p
```

### Smallest File Size
```
Format: Worst Quality (smallest)
```

### Specific Codec (VP9)
```
Custom Flags:
{
  "format": "bestvideo[vcodec^=vp9]+bestaudio/best"
}
```

## Audio Download Examples

### MP3 Audio Only (Default)
```
☑ Audio Only (MP3)
```

### High Quality FLAC Audio
```
☑ Audio Only (MP3)
Custom Flags:
{
  "format": "bestaudio",
  "postprocessors": [{
    "key": "FFmpegExtractAudio",
    "preferredcodec": "flac"
  }]
}
```

### Audio with Best Quality (no conversion)
```
Custom Flags:
{
  "format": "bestaudio",
  "postprocessors": []
}
```

## Playlist Examples

### Download Entire Playlist
```
URL: https://www.youtube.com/playlist?list=PLxxxxxxx
```

### Download First 5 Videos
```
URL: https://www.youtube.com/playlist?list=PLxxxxxxx
Playlist Start: 1
Playlist End: 5
```

### Download Videos 10-20
```
URL: https://www.youtube.com/playlist?list=PLxxxxxxx
Playlist Start: 10
Playlist End: 20
```

### Download Newest Videos First
```
Custom Flags:
{
  "playlistreverse": true
}
```

### Download Random Selection
```
Custom Flags:
{
  "playlistrandom": true,
  "playlistend": 10
}
```

## Subtitle Examples

### Download All Subtitles
```
☑ Download Subtitles
```

### Specific Language Subtitles
```
Custom Flags:
{
  "writesubtitles": true,
  "subtitleslangs": ["en", "es"]
}
```

### Auto-Generated Subtitles Only
```
Custom Flags:
{
  "writeautomaticsub": true
}
```

### Embed Subtitles in Video
```
☑ Download Subtitles
Custom Flags:
{
  "embedsubtitles": true
}
```

## Metadata & Thumbnails

### Save Video Info JSON
```
Custom Flags:
{
  "writeinfojson": true
}
```

### Download Thumbnail
```
Custom Flags:
{
  "writethumbnail": true
}
```

### Embed Thumbnail in Video
```
Custom Flags:
{
  "writethumbnail": true,
  "embedthumbnail": true
}
```

### Download Everything
```
Custom Flags:
{
  "writeinfojson": true,
  "writethumbnail": true,
  "embedthumbnail": true,
  "writesubtitles": true,
  "embedsubtitles": true,
  "writedescription": true
}
```

## File Organization Examples

### Organize by Uploader
```
Output Template: %(uploader)s/%(title)s.%(ext)s
```

### Organize by Date
```
Output Template: %(upload_date)s - %(title)s.%(ext)s
```

### Include Video ID
```
Output Template: %(title)s [%(id)s].%(ext)s
```

### Custom Format
```
Output Template: %(uploader)s - %(upload_date)s - %(title)s.%(ext)s
```

### Episode Series (Playlist Index)
```
Output Template: S01E%(playlist_index)02d - %(title)s.%(ext)s
Result: S01E01 - First Episode.mp4
```

## Platform-Specific Examples

### YouTube Channel - Latest Videos
```
URL: https://www.youtube.com/@channelname/videos
Playlist End: 10
```

### Twitter/X Video
```
URL: https://twitter.com/user/status/1234567890
Format: Best Quality
```

### Twitch VOD
```
URL: https://www.twitch.tv/videos/1234567890
Format: Best Quality
```

### Reddit Video
```
URL: https://www.reddit.com/r/videos/comments/xxxxxx/
Format: Best Quality
```

### Vimeo Private Video (with password)
```
URL: https://vimeo.com/123456789
Custom Flags:
{
  "videopassword": "your_password"
}
```

## Rate Limiting & Throttling

### Limit Download Speed to 1 MB/s
```
Custom Flags:
{
  "ratelimit": 1000000
}
```

### Throttle to 500 KB/s
```
Custom Flags:
{
  "ratelimit": 500000
}
```

### Sleep Between Downloads (for playlists)
```
Custom Flags:
{
  "sleep_interval": 5,
  "max_sleep_interval": 10
}
```

## Authentication Examples

### YouTube with Account
```
Custom Flags:
{
  "username": "your_email@gmail.com",
  "password": "your_password"
}
```

Note: For production, use cookies instead:
```
Custom Flags:
{
  "cookiefile": "/path/to/cookies.txt"
}
```

## Advanced Filter Examples

### Videos Longer than 10 Minutes
```
Custom Flags:
{
  "match_filter": "duration > 600"
}
```

### Videos from Last Week
```
Custom Flags:
{
  "dateafter": "20240101"
}
```

### Filter by View Count
```
Custom Flags:
{
  "match_filter": "view_count > 100000"
}
```

## Archival / Backup Examples

### Complete Archival Download
```
☑ Download Subtitles
Custom Flags:
{
  "writeinfojson": true,
  "writethumbnail": true,
  "writedescription": true,
  "writecomments": true,
  "getcomments": true,
  "writeannotations": true
}
Output Template: %(uploader)s/%(upload_date)s-%(title)s/%(title)s.%(ext)s
```

### Backup Playlist with Metadata
```
URL: https://www.youtube.com/playlist?list=PLxxxxxxx
☑ Download Subtitles
Custom Flags:
{
  "writeinfojson": true,
  "writethumbnail": true
}
Output Template: %(playlist_title)s/%(playlist_index)02d - %(title)s.%(ext)s
```

## Live Stream Examples

### Download Live Stream
```
URL: https://www.youtube.com/watch?v=xxxxx
Format: Best Quality
```

### Monitor for Live Stream
```
Custom Flags:
{
  "wait_for_video": 60,
  "live_from_start": true
}
```

## Performance Optimization

### Multiple Concurrent Fragments
```
Custom Flags:
{
  "concurrent_fragment_downloads": 5
}
```

### Retry on Failure
```
Custom Flags:
{
  "retries": 10,
  "fragment_retries": 10
}
```

### Buffer Size
```
Custom Flags:
{
  "buffersize": 4096
}
```

## Post-Processing Examples

### Convert to MP4 (force)
```
Custom Flags:
{
  "merge_output_format": "mp4",
  "postprocessors": [{
    "key": "FFmpegVideoConvertor",
    "preferedformat": "mp4"
  }]
}
```

### Add Chapter Markers
```
Custom Flags:
{
  "sponsorblock_mark": "all"
}
```

### Remove Sponsors (SponsorBlock)
```
Custom Flags:
{
  "sponsorblock_remove": ["sponsor", "selfpromo"]
}
```

## Troubleshooting Examples

### Ignore Errors in Playlist
```
Custom Flags:
{
  "ignoreerrors": true
}
```

### Force IPv4
```
Custom Flags:
{
  "source_address": "0.0.0.0"
}
```

### Use Specific User Agent
```
Custom Flags:
{
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
```

### Add Custom Headers
```
Custom Flags:
{
  "headers": {
    "Referer": "https://example.com"
  }
}
```

## Template Variables Reference

Common variables for Output Template:

- `%(title)s` - Video title
- `%(id)s` - Video ID
- `%(ext)s` - File extension
- `%(uploader)s` - Channel/uploader name
- `%(upload_date)s` - Upload date (YYYYMMDD)
- `%(duration)s` - Video duration
- `%(view_count)s` - View count
- `%(playlist)s` - Playlist name
- `%(playlist_index)s` - Video index in playlist
- `%(resolution)s` - Video resolution
- `%(fps)s` - Frames per second
- `%(filesize)s` - Approximate file size

See full list: https://github.com/yt-dlp/yt-dlp#output-template

---

More options available at: https://github.com/yt-dlp/yt-dlp#usage-and-options
