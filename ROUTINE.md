# Run (what the scheduled Claude session does) — UPDATED 2026-11-17

Hunter's rules: **6 feed posts every day** (TikTok, Threads, Instagram) + **10 Instagram stories every day**.
Runs 4x a day (about 2:07, 8:07, 14:07, 20:07 Vancouver) because Buffer's free plan holds only 10 scheduled items per channel
(feed posts AND stories count, see "Plan limit"). Every run is idempotent: it only does what is missing.

## Each run
1. `python -m buddha_post.verify` (PYTHONPATH=. from repo root). Look at what exists.
2. Prepare content for TODAY and TOMORROW (America/Vancouver) if `content/<date>.json` or `output/<date>/stories/` is missing:
   - Feed: write `content/<date>.json` with SIX posts in this order (times come from `config.json`: 08:00 carousel, 10:00 single,
     12:00 carousel, 15:00 single, 17:00 carousel, 20:00 single; add `"type": "single"` on singles). Carousels = 4 slides, singles = 1.
   - `python -m buddha_post.build_day <date>`; look at the slides.
   - Stories: `python -m buddha_post.build_stories <date>` (10 vertical 9:16 frames, reuses OLD quotes + `content/bank.json`; no writing needed).
3. Commit and push to `main`, wait ~10 s so the raw GitHub URLs work.
4. `python -m buddha_post.topup --live` (schedules earliest slots first on every channel until Buffer says the queue is full; that is expected, the next run continues).
5. `python -m buddha_post.verify`; it must end with `next-8h check: all slots queued`. Commit/push the updated `output/*/published*.json` if any.
6. Summary to Hunter: quotes/sources used, counts per channel per day (Vancouver + Da Nang), and anything blocked by the plan limit.

## Quote variety (Hunter, 2026-11-17: "more variety in quotes / motivational words / words of wisdom")
Per day (6 posts, 18 slides): use AT LEAST 5 different sources, and no source more than 4 times in the day. Rotate through:
Marcus Aurelius, Seneca, Epictetus, Lao Tzu, Zhuangzi, Confucius, Dhammapada/Buddhist texts, Rumi, Zen proverbs, Japanese proverbs,
Thich Nhat Hanh, Viktor Frankl, Emerson, Thoreau, Maya Angelou, plus modern psychology insights and short original motivational lines.
Styles to mix: a one-line proverb, a two-sentence wisdom, a question, a small challenge ("try one thing today..."), a gentle reminder.
Start from `content/bank.json` (verified real quotes + modern lines), but add new verified ones too.
Only REAL, verifiable quotes with the exact source in the caption (translations vary). Skip famous misattributions
(e.g. "Yesterday I was clever..." is not Rumi; "Between stimulus and response..." is not Frankl; "Luck is preparation meeting opportunity" is not Seneca).
Never reuse a feed quote from `history.json`. Stories rotate through the whole pool before repeating (`story_history.json`).

## Plan limit (free Buffer)
Free plan = 10 scheduled items per channel at once; stories count too (tested 2026-11-17). Instagram needs 16 items/day, so it is refilled by the 4 daily runs.
If `topup` reports "queue full" that is normal. If `verify` shows MISSING slots in the next 8 hours, tell Hunter: the fix is Buffer Essentials
(about $6/channel/month, unlimited queue), upgrading Instagram first.

## Content style (Hunter, 2026-11-13)
Short text on screen, 6 posts a day: 3 carousels (4 slides each) + 3 single images.
Mix REAL old-world quotes with modern psychology insights:
- Historic: only real, verifiable quotes (Marcus Aurelius, Seneca, Epictetus, Lao Tzu, Dhammapada...). Put the attribution on the slide with `||Name` after the quote text, and the exact source plus translation in the caption. Never invent or guess a "X said" line, and avoid famous misattributions.
- Psychology: short paraphrased ideas (exposure, reframing, labeling feelings, nervous-system regulation, self-compassion, small habits). No fake citations or statistics. Caption notes "General psychology ideas, not medical advice."
- Each carousel: 1 historic quote + 3 modern slides. Singles: a historic quote.
- Keep every slide under ~18 words. Never reuse a quote in `history.json`.

