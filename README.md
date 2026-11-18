# Buddha motivation posts

Makes 6 feed posts a day (3 carousels, 3 singles) + 10 Instagram stories, scheduled through Buffer to Instagram, TikTok and Threads (stories: Instagram only).

- `assets/buddha.png` — the character (transparent PNG). Used as-is, so he never changes.
- `backgrounds/` — 40 CC0 / public-domain photos; sources and licenses in `credits.json`.
  Add more with `python -m buddha_post.fetch_backgrounds "search words"`.
- `buddha_post/make_slide.py` — renders one slide (character + photo + quote).
- `buddha_post/build_day.py` — renders a day from `content/<date>.json`, tracks repeats in `history.json`.
- `buddha_post/publish.py` — schedules through Buffer (dry run unless `--live`; needs `BUFFER_API_KEY`).
- `config.json` — timezone, post times, platforms, review mode.
- `ROUTINE.md` — what the daily scheduled run does.

Requires Python 3.9+ and Pillow.
