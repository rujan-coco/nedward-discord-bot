import requests
import urllib.parse
import os
import discord

COC_API_TOKEN = os.getenv("COC_API_TOKEN")


MAX_FIELDS = 25

def get_player_stats(player_tag: str):
    if not player_tag.startswith("#"):
        player_tag = f"#{player_tag}"

    encoded_tag = urllib.parse.quote(player_tag)
    res = requests.get(
        f"https://api.clashofclans.com/v1/players/{encoded_tag}",
        headers={"Authorization": f"Bearer {COC_API_TOKEN}"}
    )

    if not res.ok:
        return None

    # TODO: Filter out Super Troops cause they're always level 1 for some reason.
    data = res.json()

    CATEGORY_WEIGHTS = {
        "troops": 5,
        "spells": 3,
        "heroEquipment": 2,
        "siegeMachines": 1,
        "heroes": 2
    }

    # Calculate rush percent as before
    category_percentages = {}
    for category, weight in CATEGORY_WEIGHTS.items():
        items = data.get(category, [])
        total_level = 0
        total_max = 0
        for obj in items:
            if obj.get("village") == "builderBase":
                continue
            total_level += obj.get("level", 0)
            total_max += obj.get("maxLevel", 0)
        category_percentages[category] = (total_level / total_max * 100) if total_max > 0 else 0

    total_weight = sum(CATEGORY_WEIGHTS.values())
    weighted_sum = sum(category_percentages[cat] * CATEGORY_WEIGHTS[cat] for cat in CATEGORY_WEIGHTS)
    max_percent = round(weighted_sum / total_weight, 1) if total_weight > 0 else 0

    total_blocks = 10
    filled_blocks = int((max_percent / 100) * total_blocks)
    progress_bar = "█" * filled_blocks + "░" * (total_blocks - filled_blocks)

    if max_percent >= 95:
        rush_status = "🏆 Maxed!"
    elif max_percent >= 80:
        rush_status = "⚔️ Nearly Maxed"
    elif max_percent >= 50:
        rush_status = "⚠️ Semi-Gay"
    else:
        rush_status = "💀 Extremely Gay"

    lines = [
        f"# Player Stats — {data['name']}",
        f"**Max-o-meter:** {max_percent}% — {rush_status} `{progress_bar}`",
    ]

    def summarize_category(title, emoji, items):
        if not items:
            return ""

        filtered = [obj for obj in items if obj.get("village") != "builderBase"]
        if not filtered:
            return ""

        total_level = sum(obj.get("level", 0) for obj in filtered)
        total_max = sum(obj.get("maxLevel", 0) for obj in filtered)
        avg_percent = (total_level / total_max * 100) if total_max > 0 else 0

        highest = max(filtered, key=lambda x: x.get("level", 0)/x.get("maxLevel", 1))
        highest_pct = highest.get("level", 0) / highest.get("maxLevel", 1) * 100
        lowest = min(filtered, key=lambda x: x.get("level", 0)/x.get("maxLevel", 1))
        lowest_pct = lowest.get("level", 0) / lowest.get("maxLevel", 1) * 100

        summary = (
            f"## {emoji} {title}\n"
            f"- Total Levels: {total_level}/{total_max} ({avg_percent:.1f}%)\n"
            f"- Highest: **{highest['name']}** at {highest_pct:.1f}%\n"
            f"- Lowest: **{lowest['name']}** at {lowest_pct:.1f}%"
        )
        return summary

    categories = [
        ("Heroes", "🦸", data.get("heroes")),
        ("Hero Equipment", "🛡️", data.get("heroEquipment")),
        ("Troops", "⚔️", data.get("troops")),
        ("Spells", "✨", data.get("spells")),
        ("Siege Machines", "🏰", data.get("siegeMachines")),
    ]

    for title, emoji, items in categories:
        summary = summarize_category(title, emoji, items)
        if summary:
            lines.append(summary)

    return "\n\n".join(lines)
