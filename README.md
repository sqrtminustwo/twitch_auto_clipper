# Twitch Auto Clipper

Automatically create Twitch clips when chat activity spikes.

Twitch Auto Clipper monitors Twitch chat and detects moments where a large number of viewers send the same emote/message within a short period of time. When activity exceeds a configurable threshold, it automatically creates a Twitch clip.

## Features

- Automatically handles Twitch OAuth token refresh
- Automatically monitors multiple Twitch streams
- Detects spikes in chat activity
- Supports custom emotes/messages as clipping triggers
- Optional 7TV emote support
- Runs each streamer independently

## How it works

```text
Twitch chat
     │
     ▼
Collect messages
     │
     ▼
Count messages / emotes
     │
     ▼
Detect activity spike
     │
     ▼
Threshold exceeded?
     │
    YES
     ▼
Create Twitch clip
     │
     ▼
Call on_clip callback
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/sqrtminustwo/twitch_auto_clipper
cd twitch_auto_clipper
```

### 2. Create your Twitch application

Create a Twitch application through the [Twitch developer console](https://dev.twitch.tv/docs/authentication/register-app).

Create a `.env` file:

```env
client_id=YOUR_CLIENT_ID
client_secret=YOUR_CLIENT_SECRET
```

### 3. Install dependencies

```bash
python -m venv myvenv
source myvenv/bin/activate
pip install -r requirements.txt
```

### 4. Start the bot

```bash
python src/main.py
```

A browser window will open to authorize the application with the required `clips:edit` permission.

## Configuration

Configure the streamers and clipping criteria in the project configuration.

The bot can:

- monitor multiple streamers simultaneously
- assign different 7TV emotes to streamers
- prioritize specific emotes
- configure the chat analysis interval
- configure the message frequency required to trigger a clip

## Roadmap

- [x] Analyze Twitch chat through IRC
- [x] Twitch OAuth authentication
- [x] Automatically create clips
- [x] Monitor multiple live streamers
- [x] Save clips to a log
- [ ] Add automated tests
- [ ] Make pip package with callback that takes Clip and constants as parameters to listener

## Why?

Manually watching an entire stream to find moments worth clipping is time-consuming.

Twitch Auto Clipper uses the audience's reaction as a signal: when chat suddenly becomes active around a particular message or emote, the bot can automatically capture the moment.
