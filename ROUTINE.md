# Daily run (what the scheduled Claude session does)

Runs once a day (currently 2:07 PM Pacific) (America/Vancouver) and prepares *tomorrow's* posts,
so Hunter has all day to review them.

1. Read `config.json` and `history.json`. Pick 3-4 themes not used in the last week
   (growth, discomfort, letting go, self-worth, patience, healing, discipline, peace, solitude, change).
2. Write `content/<tomorrow>.json`: FOUR posts per day, in this order and mix (Hunter's rule):
   post 1 (08:00) carousel (4 quotes), post 2 (12:00) SINGLE image (1 quote, add `"type": "single"`),
   post 3 (17:00) carousel (4 quotes), post 4 (20:00) SINGLE image (1 quote, `"type": "single"`).
   - Quotes are ORIGINAL, 8-30 words, plain warm voice, no clichés, no fake "Buddha said" attributions.
   - Never reuse a quote in `history.json`. Slide 1 is the hook; slide 4 lands it.
   - Caption: one or two short lines plus a soft call to action (save / share / comment). Hashtags are added automatically.
3. Render: `python -m buddha_post.build_day <tomorrow>`. Look at every slide; fix anything where text is hard to read.
4. Commit and push to `main`.
5. If `review_before_post` is true: send Hunter the slides and captions and wait for approval
   (approve all, approve some, or rewrite). Only after approval:
   `python -m buddha_post.publish <tomorrow> --live` (add `--post N` for a single post).
   If false: publish right away.
6. Record what was scheduled (the publisher writes `output/<date>/published.json`), commit and push.

Never publish anything Hunter has not approved while review mode is on.

## Posting mode (current: buffer_api, scheduled into Buffer; nothing goes live before its slot, so Hunter can review/delete in Buffer)

`config.json` -> `posting_mode`:
- `manual_upload` (current): no posting key is available to scheduled runs, so after step 4 the run sends Hunter
  the slides and captions for each post (with the target time) and Hunter uploads them in Buffer / the apps. Skip step 5's publish call.
- `buffer_api`: needs `BUFFER_API_KEY` in the run's environment and a public media URL. Not available yet.

## Which day to prepare
Run `python -m buddha_post.verify` first. Prepare the FIRST date, starting from tomorrow (America/Vancouver), whose Facebook count is below 4.
If `content/<date>.json` already exists and its slides are in `output/<date>/`, do NOT rewrite it; just run `publish <date> --live`.
`publish` is idempotent: it skips slots already in Buffer, so re-running only fills the missing ones.
Buffer's free plan allows only 10 scheduled posts at once. If publish reports the limit, the remaining slots stay unscheduled and the next run retries them. Tell Hunter the plan limit is the cause.
Hunter views Buffer in Da Nang time (Asia/Ho_Chi_Minh), so `verify` checks every day in both timezones.

## Content style (Hunter, 2026-11-13)
Short text on screen, 4 posts a day: 2 carousels (4 slides each) + 2 single images.
Mix REAL old-world quotes with modern psychology insights:
- Historic: only real, verifiable quotes (Marcus Aurelius, Seneca, Epictetus, Lao Tzu, Dhammapada...). Put the attribution on the slide with `||Name` after the quote text, and the exact source plus translation in the caption. Never invent or guess a "X said" line, and avoid famous misattributions.
- Psychology: short paraphrased ideas (exposure, reframing, labeling feelings, nervous-system regulation, self-compassion, small habits). No fake citations or statistics. Caption notes "General psychology ideas, not medical advice."
- Each carousel: 1 historic quote + 3 psychology slides. Singles: a historic quote.
- Keep every slide under ~18 words. Never reuse a quote in `history.json`.

## Always verify the count (Hunter's rule: 4 posts every day, no exceptions)
After scheduling, run `python -m buddha_post.verify <date>`. It lists what Buffer really holds for that day (Vancouver time).
If any channel has fewer than 4 posts for the day, fix it (re-run `publish --post N` only for the missing slots; never re-schedule slots that exist) and re-verify.
Buffer's web app shows times in the viewer's own timezone, so a day can look short there; trust `verify`.
