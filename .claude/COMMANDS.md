# Claude Commands for YouTube Video Fetcher

This file documents custom commands you can use with Claude to manage this project.

## Fetch Videos Command

To fetch videos from a YouTube channel, you can use any of these commands:

### Option 1: Direct command
```
fetch channel https://www.youtube.com/@ChannelName
```

### Option 2: Natural language
```
run the fetch script for https://www.youtube.com/@ChannelName
```

### Option 3: Shorthand
```
fetch https://www.youtube.com/@ChannelName
```

## What happens when you run this command:

1. Claude will execute: `python3 fetch_videos.py [YOUR_URL]`
2. The script will:
   - Fetch all videos from the channel
   - Fetch all custom playlists
   - Map videos to their playlists
   - Save results to `data/csv_outputs/[Channel_Name]_videos.csv`
   - Update `data/tracked_channels.txt` with the channel info

## Examples:

```
fetch channel https://www.youtube.com/@linuxfoundation
```

```
run fetch for https://www.youtube.com/channel/UC123456789
```

## Permissions

The `.claude/settings.local.json` file includes automatic permissions for:
- Running `python3 fetch_videos.py` with any arguments
- Git operations (add, commit)
- Creating directories
- Reading files

You won't be prompted for permission when using these commands.
