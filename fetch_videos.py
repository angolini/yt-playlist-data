#!/usr/bin/env python3
"""
YouTube Channel Video Extractor
Fetches all videos from a YouTube channel and exports to CSV
"""

import os
import sys
import csv
import re
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
API_KEY = os.getenv('YOUTUBE_API_KEY')

if not API_KEY or API_KEY == 'your_api_key_here':
    print("Error: YouTube API key not found or not configured.")
    print("Please set YOUTUBE_API_KEY in your .env file")
    print("See README.md for instructions on obtaining an API key")
    sys.exit(1)


def extract_channel_id(url):
    """
    Extract channel ID from various YouTube URL formats

    Args:
        url: YouTube channel URL

    Returns:
        Channel ID or handle/username (to be resolved later)
    """
    # Handle format: @handle
    handle_match = re.search(r'@([\w-]+)', url)
    if handle_match:
        return ('handle', handle_match.group(1))

    # Channel ID format: /channel/UC...
    channel_match = re.search(r'/channel/(UC[\w-]+)', url)
    if channel_match:
        return ('id', channel_match.group(1))

    # Custom URL format: /c/CustomName
    custom_match = re.search(r'/c/([\w-]+)', url)
    if custom_match:
        return ('custom', custom_match.group(1))

    # Username format: /user/Username
    user_match = re.search(r'/user/([\w-]+)', url)
    if user_match:
        return ('user', user_match.group(1))

    # If no pattern matches, return as-is (might be just a channel ID)
    return ('id', url)


def get_channel_id_from_handle(youtube, handle):
    """
    Resolve @handle or custom URL to channel ID

    Args:
        youtube: YouTube API client
        handle: Channel handle, custom name, or username

    Returns:
        Channel ID string
    """
    try:
        # Try searching for the channel
        request = youtube.search().list(
            part="snippet",
            q=handle,
            type="channel",
            maxResults=1
        )
        response = request.execute()

        if response['items']:
            return response['items'][0]['snippet']['channelId']
        else:
            print(f"Error: Could not find channel with handle/name: {handle}")
            sys.exit(1)
    except HttpError as e:
        print(f"Error resolving channel: {e}")
        sys.exit(1)


def get_uploads_playlist_id(youtube, channel_id):
    """
    Get the uploads playlist ID for a channel

    Args:
        youtube: YouTube API client
        channel_id: Channel ID

    Returns:
        Uploads playlist ID
    """
    try:
        request = youtube.channels().list(
            part="contentDetails,snippet",
            id=channel_id
        )
        response = request.execute()

        if not response['items']:
            print(f"Error: Channel not found: {channel_id}")
            sys.exit(1)

        channel_name = response['items'][0]['snippet']['title']
        uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        return uploads_playlist_id, channel_name
    except HttpError as e:
        print(f"Error fetching channel details: {e}")
        sys.exit(1)


def fetch_all_videos(youtube, playlist_id):
    """
    Fetch all videos from a playlist with pagination

    Args:
        youtube: YouTube API client
        playlist_id: Playlist ID

    Returns:
        List of video dictionaries with title, date, and URL
    """
    videos = []
    next_page_token = None
    page_count = 0

    print("Fetching videos...")

    while True:
        try:
            request = youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()

            page_count += 1

            for item in response['items']:
                # Extract video information
                video_id = item['contentDetails']['videoId']
                title = item['snippet']['title']

                # Parse and format date
                published_at = item['snippet']['publishedAt']
                date = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d')

                # Construct video URL
                url = f"https://www.youtube.com/watch?v={video_id}"

                videos.append({
                    'title': title,
                    'date': date,
                    'url': url
                })

            print(f"Fetched {len(videos)} videos so far...")

            # Check if there are more pages
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

        except HttpError as e:
            if e.resp.status == 403:
                print("\nError: API quota exceeded or access forbidden")
                print("If quota exceeded, please try again tomorrow")
            else:
                print(f"\nError fetching videos: {e}")
            sys.exit(1)

    print(f"Total videos fetched: {len(videos)}")
    return videos


def track_channel(channel_name, channel_id, csv_filename):
    """
    Add channel to tracking file

    Args:
        channel_name: Name of the channel
        channel_id: Channel ID
        csv_filename: Name of the CSV file created
    """
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    tracking_file = 'data/tracked_channels.txt'
    timestamp = datetime.now().strftime('%Y-%m-%d')

    try:
        with open(tracking_file, 'a', encoding='utf-8') as f:
            f.write(f"{timestamp} | {channel_name} | {channel_id} | {csv_filename}\n")
    except IOError as e:
        print(f"Warning: Could not update tracking file: {e}")


def save_to_csv(videos, channel_name):
    """
    Save videos to CSV file

    Args:
        videos: List of video dictionaries
        channel_name: Name of the channel (for filename)

    Returns:
        Filename of the created CSV
    """
    # Create data directory if it doesn't exist
    os.makedirs('data/csv_outputs', exist_ok=True)

    # Create safe filename
    safe_name = re.sub(r'[^\w\s-]', '', channel_name)
    safe_name = re.sub(r'[-\s]+', '_', safe_name)
    filename = f"data/csv_outputs/{safe_name}_videos.csv"

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Title', 'Date', 'URL', 'Status']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for video in videos:
                writer.writerow({
                    'Title': video['title'],
                    'Date': video['date'],
                    'URL': video['url'],
                    'Status': 'Not started'
                })

        return filename
    except IOError as e:
        print(f"Error writing to CSV file: {e}")
        sys.exit(1)


def main():
    """Main function"""
    # Get channel URL from command line or user input
    if len(sys.argv) > 1:
        channel_url = sys.argv[1]
    else:
        print("YouTube Channel Video Extractor")
        print("-" * 40)
        channel_url = input("Enter YouTube channel URL: ").strip()

    if not channel_url:
        print("Error: No channel URL provided")
        sys.exit(1)

    # Build YouTube API client
    try:
        youtube = build('youtube', 'v3', developerKey=API_KEY)
    except Exception as e:
        print(f"Error building YouTube API client: {e}")
        sys.exit(1)

    # Extract channel identifier
    print(f"\nProcessing channel URL: {channel_url}")
    channel_type, channel_identifier = extract_channel_id(channel_url)

    # Resolve to channel ID if needed
    if channel_type == 'id':
        channel_id = channel_identifier
    else:
        print(f"Resolving {channel_type}: {channel_identifier}")
        channel_id = get_channel_id_from_handle(youtube, channel_identifier)

    print(f"Channel ID: {channel_id}")

    # Get uploads playlist ID and channel name
    uploads_playlist_id, channel_name = get_uploads_playlist_id(youtube, channel_id)
    print(f"Channel name: {channel_name}")
    print(f"Uploads playlist ID: {uploads_playlist_id}\n")

    # Fetch all videos
    videos = fetch_all_videos(youtube, uploads_playlist_id)

    if not videos:
        print("No videos found on this channel")
        sys.exit(0)

    # Save to CSV
    print("\nSaving to CSV...")
    filename = save_to_csv(videos, channel_name)

    # Track this channel
    track_channel(channel_name, channel_id, filename)

    print(f"\nSuccess! Saved {len(videos)} videos to: {filename}")
    print(f"Channel tracked in: data/tracked_channels.txt")


if __name__ == '__main__':
    main()
