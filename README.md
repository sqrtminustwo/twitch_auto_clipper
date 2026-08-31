# twitch_auto_clipper

Twitch bot for automated clipping based on chat messages frequency, process:

1. Authorizes you trough local webserver to get token with `clips:edit` scope (will automatically refresh token before its expiry, note that refreshing can fail in which case re authorization trough webserver would be required)
2. Loads 7tv emojies for streamers from `STREAMERS` list that have 7tv id in `TWITCH_TO_SEVENTV`
3. Starts listening for chat of `STREAMERS` trough irc and count frequency of messages, emotes from `EMOTES` list have higher priority, counts for `COUNTER_INTERVAL_SECONDS`, if at the end of interval highest frequency message has count higher than `CLIPABLE_EMOTES_COUNT` uses twitch api with access token acquired in (1) to make a clip
4. Saves all clips and timestamps in `logs/log[date].csv`

## Conventions

- Files that define classes are capitalized and do not contain `_`
- Files that define functions / variables are lower case and can contain `_`
- Variables passed to class constructor will be saved in class
- Constant variables are upper case
- Private class members start with `__`

## Used libraries

- `re` for regex matching urls and messages
- `requests` for working with apis
- `logging` (guess)
- `socket` for irc connection to twitch
- `sortedcollections` for storing words from messages in value (counter) sorted dictionary
- `threading` for webserver and threads for streamers
- `contextlib` for `ProtectedVar` contextmanager
- `datetime` (guess)
- `dotenv` and `os` for .env variables loading
- `webbrowser` to open browser and authorize with twitch for clipping
- `csv` for logging of clips
- `time` for sleeping before clipping

## Roadmap

- [x] Analyse chat trough irc
- [x] Get tokens with twitch api
- [ ] Make clips from snapshot write to log
- [ ] Wait for streamers from list to go live -> clips (for each streamer different thread)
- [ ] Automate clip processing
- [ ] agi
