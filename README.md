# twitch_auto_clipper

Automatically create Twitch clips when chat activity spikes.

Twitch Auto Clipper monitors Twitch chat and detects moments where a large number of viewers send the same emote/message within a short period of time. When activity exceeds a configurable threshold, it automatically creates a Twitch clip.

[demo]

## Installation

```bash
pip install twitch_auto_clipper
```

## Requirements

Minimum Python version supported by `twitch_auto_clipper` is 3.8.

## Quick start

```python

from twitch_auto_clipper import TwitchAutoClipper

clipper = TwitchAutoClipper(
    ["Marlon", "Lacy"],
    "YOUR_CLIENT_ID",
    "YOUR_CLIENT_SECRET",
    on_clip=lambda clip: print(clip),
    common_value=1,
    emote_value=2,
    clipable_message_ratio=0.5,
)

clipper.start()
clipper.join()
```

> [!NOTE]
> In case multiple streamers are given, `on_clip` will be called from multiple threads. Keep that in mind and use the appropriate [threading](https://docs.python.org/3/library/threading.html) Python API there.

> [!IMPORTANT]
> `client_id` and `client_secret` are saved in [TwitchAuthTokens](https://github.com/sqrtminustwo/twitch_auto_clipper/blob/40571716c73c95119f9743ba190808602a953f68/twitch_auto_clipper/auth/TwitchAuthTokens.py) and only sent to the Twitch API. Of course, you are encouraged to skim through the code to make sure your credentials are not sent where you do not want them to be sent.

> [!IMPORTANT]
> Upon initialization of [TwitchAutoClipper](https://github.com/sqrtminustwo/twitch_auto_clipper/blob/40571716c73c95119f9743ba190808602a953f68/twitch_auto_clipper/TwitchAutoClipper.py), your web browser should open to gain clipping permission for your Twitch account (as shown in the demo). The code responsible for this is also in [TwitchAuthTokens](https://github.com/sqrtminustwo/twitch_auto_clipper/blob/40571716c73c95119f9743ba190808602a953f68/twitch_auto_clipper/auth/TwitchAuthTokens.py). Note that it is not necessary to keep this tab open after initialization is complete for the script to work properly.

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
