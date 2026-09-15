import os
import json
import requests
from bs4 import BeautifulSoup

URL = "https://tibiaidle.com/charbazar.php"
STATE_FILE = "known_characters.json"

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]


def get_characters():
    response = requests.get(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=30
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    characters = {}

    for row in soup.find_all("tr"):
        cells = row.find_all("td")

        if len(cells) < 2:
            continue

        values = [
            cell.get_text(" ", strip=True)
            for cell in cells
        ]

        name = values[0]

        if not name or name.lower() in ["name", "character"]:
            continue

        characters[name] = values

    return characters


def send_discord(message):
    response = requests.post(
        WEBHOOK_URL,
        json={"content": message},
        timeout=30
    )
    response.raise_for_status()


def load_previous():
    if not os.path.exists(STATE_FILE):
        return None

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_current(characters):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(
            characters,
            f,
            ensure_ascii=False,
            indent=2
        )


def main():
    current = get_characters()
    previous = load_previous()

    # Pierwsze uruchomienie:
    # zapamiętujemy aktualną listę bez wysyłania alertów.
    if previous is None:
        save_current(current)
        print(f"Pierwsze uruchomienie. Zapamiętano {len(current)} postaci.")
        return

    new_names = [
        name for name in current
        if name not in previous
    ]

    for name in new_names:
        values = current[name]

        message = (
            "🔔 **NOWA POSTAĆ NA TIBIA BAZAR!**\n\n"
            f"**{name}**\n"
            f"{' | '.join(values[1:])}\n\n"
            f"🔗 {URL}"
        )

        send_discord(message)

    save_current(current)

    print(
        f"Sprawdzono bazar. "
        f"Postaci: {len(current)}, "
        f"nowych: {len(new_names)}"
    )


if __name__ == "__main__":
    main()
