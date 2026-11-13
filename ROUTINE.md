# Daily run (what the scheduled Claude session does)

Runs once a day at 6:00 AM Pacific (America/Vancouver) and prepares *tomorrow's* posts,
so Hunter has all day to review them.

1. Read `config.json` and `history.json`. Pick 3-4 themes not used in the last week
   (growth, discomfort, letting go, self-worth, patience, healing, discipline, peace, solitude, change).
2. Write `content/<tomorrow>.json`: one post per theme, 4 slides each.
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

## Posting mode
`config.json` -> `posting_mode`:
- `manual_upload` (current): no posting key is available to scheduled runs, so after step 4 the run sends Hunter
  the slides and captions for each post (with the target time) and Hunter uploads them in Buffer / the apps. Skip step 5's publish call.
- `buffer_api`: needs `BUFFER_API_KEY` in the run's environment and a public media URL. Not available yet.
