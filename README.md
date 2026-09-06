[![Unit Tests](https://github.com/sqrtminustwo/twitch_auto_clipper/actions/workflows/test_runner.yml/badge.svg?branch=main)](https://github.com/sqrtminustwo/twitch_auto_clipper/actions/workflows/test_runner.yml)

# twitch_auto_clipper

Automatically create Twitch clips when chat activity spikes.

Twitch Auto Clipper monitors Twitch chat and detects moments where a large number of viewers send the same emote/message within a short period of time. When activity exceeds a configurable threshold, it automatically creates a Twitch clip.

[demo]

## Installation

```bash
pip install twitch_auto_clipper
```

## Requirements

Minimum Python version supported by `twitch_auto_clipper` is 3.10.

## Quick start

````python

[![Unit Tests](https://github.com/sqrtminustwo/twitch_auto_clipper/actions/workflows/test_runner.yml/badge.svg?branch=main)](https://github.com/sqrtminustwo/twitch_auto_clipper/actions/workflows/test_runner.yml)

# twitch_auto_clipper

Automatically create Twitch clips when chat activity spikes.

Twitch Auto Clipper monitors Twitch chat and detects moments where a large number of viewers send the same emote/message within a short period of time. When activity exceeds a configurable threshold, it automatically creates a Twitch clip.

[demo]

## Installation

```bash
pip install twitch_auto_clipper
````

## Requirements

Minimum Python version supported by `twitch_auto_clipper` is 3.10.

## Quick start

```python
from twitch_auto_clipper_sqrtminusone.TwitchAutoClipper import TwitchAutoClipper

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

> [!IMPORTANT]
> `client_id` and `client_secret` are saved in [TwitchAuthTokens](twitch_auto_clipper_sqrtminusone/auth/TwitchAuthTokens.py) and only sent to the Twitch API.

> [!IMPORTANT]
> Upon initialization of [TwitchAutoClipper](twitch_auto_clipper_sqrtminusone/TwitchAutoClipper.py), your web browser should open to gain clipping permission for your Twitch account (as shown in the demo).

## Features

- Automatically handles Twitch OAuth token refresh
- Automatically monitors multiple Twitch streams
- Supports custom emotes/messages as clipping triggers
- Optional 7TV emote support
- Runs each streamer in separate thread

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

## Usage

There are two classes that you will typically need:

- `TwitchAutoClipper` — monitors Twitch chat and automatically creates clips when a message reaches the configured threshold.
- `Clip` — contains information about a clip that was created.

### `TwitchAutoClipper`

```python
TwitchAutoClipper(
    streamers_names,
    client_id,
    client_secret,
    on_clip,
    counter_interval_seconds=...,
    clipable_message_ratio=...,
    clipable_wait=...,
    common_value=...,
    emote_value=...,
    excluded_words=...,
    logging_handlers=...,
    logging_level=...
)
```

| Argument                   | Description                                                                                                                                                                                                                              |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `streamers_names`          | List of Twitch usernames to monitor. Usernames are case-insensitive and are converted to lowercase.                                                                                                                                      |
| `client_id`                | Your Twitch application client ID. Available from the [Twitch Developer Console](https://dev.twitch.tv/docs/authentication/register-app).                                                                                                |
| `client_secret`            | Your Twitch application client secret. Available from the [Twitch Developer Console](https://dev.twitch.tv/docs/authentication/register-app).                                                                                            |
| `on_clip`                  | Callback function invoked with a `Clip` instance when a clip is created.                                                                                                                                                                 |
| `counter_interval_seconds` | Time interval over which chat message frequencies are counted. Once the interval ends, the counters are reset.                                                                                                                           |
| `clipable_message_ratio`   | The weighted frequency of the most frequent message divided by the total number of messages received during the current interval. Because messages can have different values (`common_value` and `emote_value`), the ratio can exceed 1. |
| `clipable_wait`            | Time to wait before creating a clip after a message reaches the clipping threshold. The waiting and clipping are performed in a separate thread, so this does not block the streamer thread.                                             |
| `common_value`             | Value assigned to a regular chat message. A regular message is any message that is not a 7TV emote when the streamer has a 7TV profile.                                                                                                  |
| `emote_value`              | Value assigned to a 7TV emote.                                                                                                                                                                                                           |
| `excluded_words`           | Words that should be excluded from message frequency counting.                                                                                                                                                                           |
| `logging_handlers`         | Logging handlers used by the package. See [`examples/logger.py`](examples/logger.py) for an example using multiple handlers.                                                                                                             |
| `logging_level`            | Logging level used by the package. See the [Python logging documentation](https://docs.python.org/3/library/logging.html#logging-levels).                                                                                                |

> [!NOTE]
> If multiple streamers are configured, `on_clip` may be called concurrently from multiple threads. Make sure your callback is thread-safe and use the appropriate [Python threading APIs](https://docs.python.org/3/library/threading.html) when necessary.

### `Clip`

A `Clip` instance contains information about the clip that was created.

| Attribute        | Description                                                                                                                                        |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `message`        | The chat message that triggered the clip.                                                                                                          |
| `message_count`  | Number of occurrences of the triggering message.                                                                                                   |
| `ratio`          | Ratio of the triggering message to the total number of messages received during the counting interval.                                             |
| `broadcaster_id` | Twitch broadcaster ID of the streamer for whom the clip was created. See the [Twitch API documentation](https://dev.twitch.tv/docs/api/reference). |
| `url`            | URL of the created clip.                                                                                                                           |
| `timestamp`      | Expected timestamp of the event highlighted by the clip.                                                                                           |
| `duration`       | Clip duration in seconds.                                                                                                                          |

## Motivation

Manually watching an entire stream to find moments worth clipping is time-consuming.

`twitch_auto_clipper` uses the audience's reaction as a signal: when chat suddenly becomes active around a particular message or emote, the bot can automatically capture the moment.

## Roadmap

- [x] Analyze Twitch chat through IRC
- [x] Twitch OAuth authentication
- [x] Automatically create clips
- [x] Monitor multiple live streamers
- [x] Save clips to a log
- [x] Add automated tests
- [ ] Pip package
- [ ] Web page for constants editing
