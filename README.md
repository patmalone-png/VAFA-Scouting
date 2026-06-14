# VAFA Women's Tracker

A GitHub Pages app that displays VAFA Premier B Women and Division 1 Women best players and goal kickers by round.

## What this repo includes
- `index.html` — static app for browsing the data
- `data/matches.json` — scraped match data used by the app
- `scripts/scrape_vafa.py` — scraper starter script
- `.github/workflows/scrape.yml` — scheduled GitHub Action to refresh the data

## How to use
1. Create a new GitHub repository.
2. Upload all files from this folder.
3. In `scripts/scrape_vafa.py`, replace `PASTE_ROUND_URL_HERE` with your competition fixture/results URLs.
4. Push to GitHub.
5. In GitHub, enable Pages from the main branch.
6. Run the workflow manually once from the Actions tab.

## Important note
The scraper currently uses heuristic selectors because the VAFA match pages are dynamically rendered and may vary by page structure. You will likely need to inspect one real match page and tighten the CSS selectors in `parse_match_page()`.

## Suggested next step
Start with one round and one competition, confirm the exact HTML structure for a match page, then refine the parser before scaling to the full season.
