# YouTube Channel Video Extractor

A Python script to extract all videos from a YouTube channel and export them to a CSV file with video title, publication date, and URL.

## Prerequisites

- Python 3.6 or higher
- A YouTube Data API v3 key

## Getting a YouTube API Key

Follow these steps to obtain your free YouTube Data API key:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Create a new project:
   - Click on the project dropdown at the top
   - Click "New Project"
   - Enter a project name (e.g., "YouTube Video Extractor")
   - Click "Create"
4. Enable the YouTube Data API v3:
   - In the search bar, type "YouTube Data API v3"
   - Click on "YouTube Data API v3" from the results
   - Click "Enable"
5. Create credentials:
   - Click "Create Credentials" button
   - Select "API Key"
   - Copy the generated API key
6. (Optional but recommended) Restrict your API key:
   - Click "Edit API key"
   - Under "API restrictions", select "Restrict key"
   - Check "YouTube Data API v3"
   - Click "Save"

## Installation

1. Clone or download this repository

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project directory:
```bash
cp .env.example .env
```

4. Edit the `.env` file and add your YouTube API key:
```
YOUTUBE_API_KEY=your_actual_api_key_here
```

## Usage

Run the script with a YouTube channel URL:

```bash
python fetch_videos.py
```

The script will prompt you to enter a YouTube channel URL. You can use any of these formats:
- `https://www.youtube.com/@ChannelHandle`
- `https://www.youtube.com/channel/UC...`
- `https://www.youtube.com/c/CustomName`
- `https://www.youtube.com/user/Username`

Or provide the URL as a command-line argument:

```bash
python fetch_videos.py "https://www.youtube.com/@ChannelHandle"
```

## Output

The script will create a CSV file named `{channel_name}_videos.csv` with the following columns:
- **Title**: The video title
- **Date**: Publication date in YYYY-MM-DD format
- **URL**: Direct link to the video

Example output:
```csv
Title,Date,URL
"Getting Started with Python","2024-01-15","https://www.youtube.com/watch?v=abc123"
"Advanced Python Tips","2024-01-20","https://www.youtube.com/watch?v=def456"
```

## API Quota Information

The YouTube Data API has a quota limit of 10,000 units per day for free tier:
- Each `playlistItems.list` request costs 1 unit
- Each `channels.list` request costs 1 unit
- Fetching 1000 videos requires approximately 21 units

Most channels can be fully fetched within the free daily quota.

## Troubleshooting

**Error: "API key not found"**
- Make sure you created the `.env` file and added your API key

**Error: "Invalid API key"**
- Verify your API key is correct in the `.env` file
- Check that YouTube Data API v3 is enabled in Google Cloud Console

**Error: "Quota exceeded"**
- You've hit the daily API quota limit (10,000 units)
- Wait until the next day (quota resets at midnight Pacific Time)

**Error: "Channel not found"**
- Verify the channel URL is correct
- Some private or terminated channels cannot be accessed
