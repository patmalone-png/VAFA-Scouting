import json
import re
from pathlib import Path
from typing import List, Dict

import requests
from bs4 import BeautifulSoup

OUT = Path(__file__).resolve().parents[1] / 'data' / 'matches.json'

SEEDS = [
    {
        'competition': 'Premier B Women',
        'round_url': 'https://www.vafa.com.au/football/results/scores/?type=results&grade_id=972de8ed-8555-42ce-91de-660850b3e7ea&session_id=2af0bc11-6f71-4c82-93b5-d46fe9bc739f&season=2026&Round=1'
    },
    {
        'competition': 'Division 1 Women',
        'round_url': 'PASTE_ROUND_URL_HERE'
    }
]

HEADERS = {'User-Agent': 'Mozilla/5.0'}


def get(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text


def parse_goal_text(text: str) -> List[Dict]:
    items = []
    for part in [p.strip() for p in text.split(',') if p.strip()]:
        m = re.match(r'^(.*?)\s+(\d+)$', part)
        if m:
            items.append({'player': m.group(1).strip(), 'goals': int(m.group(2))})
        else:
            items.append({'player': part, 'goals': 1})
    return items


def extract_match_links(round_html: str, base: str) -> List[str]:
    soup = BeautifulSoup(round_html, 'html.parser')
    links = []
    for a in soup.select('a[href]'):
        href = a['href']
        if 'match' in href.lower() or 'fixture' in href.lower():
            if href.startswith('http'):
              links.append(href)
            elif href.startswith('/'):
              links.append(base.rstrip('/') + href)
    return sorted(set(links))


def parse_match_page(html: str, competition: str) -> List[Dict]:
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text('\n', strip=True)
    title = soup.title.string.strip() if soup.title and soup.title.string else 'Unknown Match'

    round_match = re.search(r'Round\s+(\d+)', text, re.I)
    round_no = int(round_match.group(1)) if round_match else None

    records = []

    # Heuristic placeholders: adjust selectors once real match HTML is confirmed.
    sections = soup.select('[class*="team"], [class*="match"], table, section')
    for block in sections:
        block_text = block.get_text(' ', strip=True)
        if 'Best' not in block_text and 'Goal' not in block_text:
            continue
        team_match = re.search(r'^(.*?)\s+Best', block_text)
        team = team_match.group(1).strip() if team_match else 'Unknown Team'
        best_match = re.search(r'Best(?:\s+Players?)?\s*[:\-]\s*(.*?)\s+Goal', block_text, re.I)
        goals_match = re.search(r'Goal(?:\s+Kickers?)?\s*[:\-]\s*(.*)$', block_text, re.I)
        best_players = [p.strip() for p in re.split(r',|;', best_match.group(1)) if p.strip()] if best_match else []
        goal_kickers = parse_goal_text(goals_match.group(1)) if goals_match else []
        if best_players or goal_kickers:
            records.append({
                'competition': competition,
                'round': round_no,
                'match': title,
                'team': team,
                'best_players': best_players,
                'goal_kickers': goal_kickers
            })
    return records


def main():
    all_rows = []
    for seed in SEEDS:
        if 'PASTE_ROUND_URL_HERE' in seed['round_url']:
            continue
        html = get(seed['round_url'])
        links = extract_match_links(html, 'https://www.vafa.com.au')
        for link in links:
            try:
                match_html = get(link)
                all_rows.extend(parse_match_page(match_html, seed['competition']))
            except Exception:
                continue
    OUT.write_text(json.dumps(all_rows, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
