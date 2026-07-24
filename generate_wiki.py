#!/usr/bin/env python3
"""
Generate index.html for CCE Wiki from Lua data files.
Flat grid layout grouped by cosmic sphere, matching the in-game browse-all screen.
"""
import re
import html
import os
from collections import defaultdict

LUA_DIR = r"C:\Users\beren\Objet\wow_addon\ClassicClassesEnhanced"
OUT_FILE = r"C:\Users\beren\Objet\cce-wiki\index.html"

# ── Sphere definitions (matching CatalogUI.lua) ──
SPHERE_ORDER = ["light", "life", "chaos", "reality", "order", "death", "shadow"]

SPHERE_COLORS = {
    "light":   "#fff2b0",
    "life":    "#7ec850",
    "chaos":   "#50e650",
    "reality": "#c8a862",
    "order":   "#5cc0e8",
    "death":   "#b060d8",
    "shadow":  "#7848b0",
}

SPHERE_NAMES = {
    "light":   "Light",
    "life":    "Life",
    "chaos":   "Chaos",
    "reality": "Reality",
    "order":   "Order",
    "death":   "Death",
    "shadow":  "Shadow",
}

CLASS_SPHERE = {
    "Beastmaster":        "reality",
    "Berserker":          "reality",
    "Barbarian":          "reality",
    "Mountaineer":        "reality",
    "Ranger":             "reality",
    "Mountain King":      "reality",
    "Brewmaster":         "reality",
    "Wilderness Stalker": "reality",
    "Prospector":         "reality",
    "Buccaneer":          "reality",
    "Brave":              "reality",
    "Death Knight":       "shadow",
    "Twilight Cultist":   "shadow",
    "Lightslayer":        "shadow",
    "Hexxer":             "shadow",
    "Shadow Hunter":      "shadow",
    "Witch Doctor":       "shadow",
    "Plagueshifter":      "life",
    "Earthcaller":        "life",
    "Warden":             "life",
    "Savagekin":          "life",
    "Elven Archer":       "life",
    "Druid of the Claw":  "life",
    "Druid of the Wild":  "life",
    "Dragonsworn":        "life",
    "Techno-mage":        "order",
    "Ley Walker":         "order",
    "Runemaster":         "order",
    "Sister of Steel":    "order",
    "Kirin Tor Mage":     "order",
    "Spellblade":         "order",
    "Tinker":             "order",
    "Scarlet Champion":   "light",
    "Moon Priest":        "light",
    "Exemplar":           "light",
    "Templar":            "light",
    "Shieldbearer":       "light",
    "Apothecary":         "death",
    "Necromancer":        "death",
    "Spiritwalker":       "death",
    "Spirit Champion":    "death",
    "Bloodmage":          "chaos",
    "Pyremaster":         "chaos",
    "Hedge Wizard":       "chaos",
    "Blademaster":        "chaos",
    "Demon Hunter":       "chaos",
}

# ── Portrait filename mapping (display name → PNG in icons/) ──
PORTRAIT_MAP = {
    "Apothecary":         "Apothecary_PRIEST.jpg",
    "Beastmaster":        "Beastmaster_HUNTER.jpg",
    "Berserker":          "Berserker_ROGUE.jpg",
    "Blademaster":        "Blademaster_SHAMAN.jpg",
    "Bloodmage":          "Bloodmage_MAGE.jpg",
    "Brave":              "Brave_HUNTER.jpg",
    "Brewmaster":         "Brewmaster_WARRIOR.jpg",
    "Buccaneer":          "Buccaneer_HUNTER.jpg",
    "Dark Ranger":        "Dark_Ranger_ROGUE.jpg",
    "Death Knight":       "Death_Knight_WARLOCK.jpg",
    "Demon Hunter":       "Demon_Hunter_ROGUE.jpg",
    "Dragonsworn":        "Dragonsworn_DRUID.jpg",
    "Druid of the Claw":  "Druid_of_the_Claw_DRUID.jpg",
    "Druid of the Wild":  "Druid_of_the_Wild_DRUID.jpg",
    "Earthcaller":        "Earthcaller_SHAMAN.jpg",
    "Elven Ranger":       "Elven_Ranger_HUNTER.jpg",
    "Exemplar":           "Exemplar_PALADIN.jpg",
    "Gladiator":          "Gladiator_ROGUE.jpg",
    "Hedge Wizard":       "Hedge_Wizard_MAGE.jpg",
    "Huntress":           "Huntress_WARRIOR.jpg",
    "Kirin Tor Mage":     "Kirin_Tor_Mage_MAGE.jpg",
    "Ley Walker":         "Ley_Walker_MAGE.jpg",
    "Lightslayer":        "Lightslayer_PRIEST.jpg",
    "Moon Priestess":     "Moon_Priestess_PRIEST.jpg",
    "Mountain King":      "Mountain_King_ROGUE.jpg",
    "Mountaineer":        "Mountaineer_HUNTER.jpg",
    "Necromancer":        "Necromancer_WARLOCK.jpg",
    "Plagueshifter":      "Plagueshifter_DRUID.jpg",
    "Prospector":         "Prospector_ROGUE.jpg",
    "Pyremaster":         "Pyremaster_SHAMAN.jpg",
    "Runemaster":         "Runemaster_WARRIOR_ALLIANCE.jpg",
    "Savagekin":          "Savagekin_DRUID.jpg",
    "Scarlet Champion":   "Scarlet_Champion_PALADIN.jpg",
    "Shadow Hunter":      "Shadow_Hunter_HUNTER.jpg",
    "Shieldbearer":       "Shieldbearer_PALADIN.jpg",
    "Sister of Steel":    "Sister_of_Steel_PALADIN.jpg",
    "Spellblade":         "Spellblade_MAGE_ALLIANCE.jpg",
    "Spiritwalker":       "Spiritwalker_SHAMAN.jpg",
    "Techno-mage":        "Techno-mage_MAGE.jpg",
    "Templar":            "Templar_PALADIN.jpg",
    "Tinker":             "Tinker_ROGUE.jpg",
    "Twilight Cultist":   "Twilight_Cultist_PRIEST.jpg",
    "Warden":             "Warden_ROGUE.jpg",
    "Wilderness Stalker": "Wilderness_Stalker_HUNTER.jpg",
    "Witch Doctor":       "Witch_Doctor_PRIEST.jpg",
}

RACE_ORDER = ["Human", "Dwarf", "Night Elf", "Gnome", "Orc", "Troll", "Tauren", "Undead"]
RACE_FACTION = {
    "Human": "alliance", "Dwarf": "alliance", "Night Elf": "alliance", "Gnome": "alliance",
    "Orc": "horde", "Troll": "horde", "Tauren": "horde", "Undead": "horde",
}

RACE_CLASSES = {
    "Human":     ["WARRIOR", "PALADIN", "ROGUE", "PRIEST", "MAGE", "WARLOCK"],
    "Dwarf":     ["WARRIOR", "PALADIN", "HUNTER", "ROGUE", "PRIEST"],
    "Night Elf": ["WARRIOR", "HUNTER", "ROGUE", "PRIEST", "DRUID"],
    "Gnome":     ["WARRIOR", "ROGUE", "MAGE", "WARLOCK"],
    "Orc":       ["WARRIOR", "HUNTER", "ROGUE", "SHAMAN", "WARLOCK"],
    "Troll":     ["WARRIOR", "HUNTER", "ROGUE", "PRIEST", "SHAMAN", "MAGE"],
    "Tauren":    ["WARRIOR", "HUNTER", "SHAMAN", "DRUID"],
    "Undead":    ["WARRIOR", "ROGUE", "PRIEST", "MAGE", "WARLOCK"],
}

CLASS_DISPLAY_ORDER = ["WARRIOR", "PALADIN", "HUNTER", "ROGUE", "PRIEST", "SHAMAN", "MAGE", "WARLOCK", "DRUID"]
CLASS_COLORS = {
    "WARRIOR": "#C69B6D", "PALADIN": "#F48CBA", "HUNTER": "#AAD372",
    "ROGUE": "#FFF468", "PRIEST": "#FFFFFF", "SHAMAN": "#0070DD",
    "MAGE": "#3FC7EB", "WARLOCK": "#8788EE", "DRUID": "#FF7C0A",
}

TALENT_TREES = {
    "WARRIOR": {1: "Arms", 2: "Fury", 3: "Protection"},
    "ROGUE": {1: "Assassination", 2: "Combat", 3: "Subtlety"},
    "WARLOCK": {1: "Affliction", 2: "Demonology", 3: "Destruction"},
    "DRUID": {1: "Balance", 2: "Feral", 3: "Restoration"},
    "HUNTER": {1: "Beast Mastery", 2: "Marksmanship", 3: "Survival"},
    "SHAMAN": {1: "Elemental", 2: "Enhancement", 3: "Restoration"},
    "PALADIN": {1: "Holy", 2: "Protection", 3: "Retribution"},
    "PRIEST": {1: "Discipline", 2: "Holy", 3: "Shadow"},
    "MAGE": {1: "Arcane", 2: "Fire", 3: "Frost"},
}


# ── File / Lua parsing ──

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def extract_braced_block(text, start_pos):
    depth = 1
    pos = start_pos
    while pos < len(text) and depth > 0:
        ch = text[pos]
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
        elif ch == '"':
            pos += 1
            while pos < len(text) and text[pos] != '"':
                if text[pos] == '\\':
                    pos += 1
                pos += 1
        elif ch == '-' and pos + 1 < len(text) and text[pos + 1] == '-':
            while pos < len(text) and text[pos] != '\n':
                pos += 1
        pos += 1
    return text[start_pos:pos - 1]


def parse_lore_data(text):
    lore = {}
    for m in re.finditer(r'\["([^"]+)"\]\s*=\s*"((?:[^"\\]|\\.)*)"', text):
        name = m.group(1)
        lore_text = m.group(2).replace('\\"', '"').replace("\\'", "'").replace("\\n", "\n")
        lore[name] = lore_text
    return lore


def parse_talent_requirements(text):
    """Parse talent requirements keyed by CLASS_Spec (e.g. WARRIOR_Slam)."""
    talents = {}
    current_key = None
    current_roles = None
    for line in text.split("\n"):
        # Match both ["KEY"] and ['KEY'] formats
        m = re.match(r"""\s*\[['"]([^'"]+)['"]\]\s*=\s*\{""", line)
        if m:
            current_key = m.group(1)
            talents[current_key] = {"entries": [], "roles": None}
            # Check for roles on same line
            rm = re.search(r'roles\s*=\s*"([^"]*)"', line)
            if rm:
                talents[current_key]["roles"] = rm.group(1)
            continue
        if current_key is not None:
            rm = re.search(r'roles\s*=\s*"([^"]*)"', line)
            if rm:
                talents[current_key]["roles"] = rm.group(1)
            m = re.match(r'\s*R\("([^"]+)",\s*(\d+),\s*(\d+),\s*(\d+)(?:,\s*(\d+))?\)', line)
            if m:
                talents[current_key]["entries"].append({
                    "name": m.group(1),
                    "tab": int(m.group(2)),
                    "rank": int(m.group(3)),
                    "level": int(m.group(4)),
                    "endLevel": int(m.group(5)) if m.group(5) else None,
                })
            if re.match(r'\s*\},?\s*$', line) and not re.match(r'\s*R\(', line):
                current_key = None
    return talents


def parse_q_from_text(text):
    quests = []
    for qm in re.finditer(r'Q\("((?:[^"\\]|\\.)*)",\s*(\d+),\s*(\d+)\)', text):
        quests.append({
            "name": qm.group(1).replace("\\'", "'").replace('\\"', '"'),
            "level": int(qm.group(2)),
            "questID": int(qm.group(3)),
        })
    return quests


def parse_character_data(text):
    challenge_descs = {}
    cd_start = text.find("CCE.ChallengeDescriptions")
    if cd_start >= 0:
        brace = text.find("{", cd_start)
        cd_block = extract_braced_block(text, brace + 1)
        for m in re.finditer(r'\["([^"]+)"\]\s*=\s*"((?:[^"\\]|\\.)*)"', cd_block):
            challenge_descs[m.group(1)] = m.group(2).replace('\\"', '"').replace("\\'", "'")

    characters = {}
    chars_start = text.find("CCE.Characters = {")
    if chars_start < 0:
        return characters, challenge_descs

    chars_brace = text.find("{", chars_start)
    chars_text = text[chars_brace + 1:]

    char_pattern = re.compile(r'\["([^"]+)"\]\s*=\s*\{')
    char_matches = []
    for m in char_pattern.finditer(chars_text):
        name = m.group(1)
        block_start = m.end()
        peek = chars_text[block_start:block_start + 200]
        if 'class' in peek and any(c in peek for c in
                ['WARRIOR', 'ROGUE', 'WARLOCK', 'DRUID', 'HUNTER', 'SHAMAN', 'PALADIN', 'PRIEST', 'MAGE']):
            char_matches.append((name, block_start))

    for i, (name, start) in enumerate(char_matches):
        block = extract_braced_block(chars_text, start)
        char = parse_single_char(name, block)
        if char:
            characters[name] = char

    return characters, challenge_descs


def parse_single_char(name, block):
    char = {"key": name}

    # Split Name_CLASS key into display name and class
    parts = name.rsplit("_", 1)
    if len(parts) == 2 and parts[1] in ("WARRIOR", "ROGUE", "WARLOCK", "DRUID", "HUNTER", "SHAMAN", "PALADIN", "PRIEST", "MAGE"):
        char["name"] = parts[0]
        char["class"] = parts[1]
    else:
        # Fallback: read class from block
        char["name"] = name
        cm = re.search(r'class\s*=\s*"([^"]*)"', block)
        char["class"] = cm.group(1) if cm else "UNKNOWN"

    # Parse races list
    rm = re.search(r'races\s*=\s*\{([^}]+)\}', block)
    if rm:
        char["races"] = re.findall(r'"([^"]+)"', rm.group(1))
    else:
        char["races"] = []

    for field in ["spec", "race", "gender", "questTheme", "gameplay"]:
        m = re.search(rf'^\s*{field}\s*=\s*"([^"]*)"', block, re.MULTILINE)
        if m:
            char[field] = m.group(1)

    # Also read class from block in case key parsing differs
    cm = re.search(r'^\s*class\s*=\s*"([^"]*)"', block, re.MULTILINE)
    if cm:
        char["class"] = cm.group(1)

    m = re.search(r'^\s*selfFound\s*=\s*(true|false)', block, re.MULTILINE)
    if m:
        char["selfFound"] = m.group(1) == "true"

    m = re.search(r'selfFoundByFaction\s*=\s*\{', block)
    if m:
        sf_block = extract_braced_block(block, m.end())
        alliance_m = re.search(r'Alliance\s*=\s*(true|false)', sf_block)
        horde_m = re.search(r'Horde\s*=\s*(true|false)', sf_block)
        if alliance_m and horde_m:
            a = alliance_m.group(1) == "true"
            h = horde_m.group(1) == "true"
            if a and not h:
                char["selfFound"] = "Alliance only"
            elif not a and h:
                char["selfFound"] = "Horde only"
            elif a and h:
                char["selfFound"] = True
            else:
                char["selfFound"] = False

    char["professions"] = []
    m = re.search(r'^\s*professions\s*=\s*\{([^}]*)\}', block, re.MULTILINE)
    if m:
        char["professions"] = re.findall(r'"([^"]+)"', m.group(1))

    m = re.search(r'recommendedProfession\s*=\s*\{', block)
    if m:
        rp_block = extract_braced_block(block, m.end())
        nm = re.search(r'name\s*=\s*"([^"]*)"', rp_block)
        rm = re.search(r'reason\s*=\s*"((?:[^"\\]|\\.)*)"', rp_block)
        if nm and rm:
            char["recommendedProfession"] = {
                "name": nm.group(1),
                "reason": rm.group(1).replace('\\"', '"').replace("\\'", "'"),
            }

    char["equipment"] = parse_e_field(block, "equipment")
    char["challenges"] = parse_e_field(block, "challenges")
    char["optionalChallenges"] = parse_e_field(block, "optionalChallenges")
    char["quests"] = parse_q_field(block, "quests")

    m = re.search(r'questsByFaction\s*=\s*\{', block)
    if m:
        faction_block = extract_braced_block(block, m.end())
        char["questsByFaction"] = {}
        for faction in ["Alliance", "Horde"]:
            fm = re.search(rf'{faction}\s*=\s*\{{', faction_block)
            if fm:
                fb = extract_braced_block(faction_block, fm.end())
                dm = re.search(r'default\s*=\s*\{', fb)
                if dm:
                    db = extract_braced_block(fb, dm.end())
                    char["questsByFaction"][faction] = parse_q_from_text(db)
                else:
                    char["questsByFaction"][faction] = parse_q_from_text(fb)

    m = re.search(r'questsByHomebound\s*=\s*\{', block)
    if m:
        hb_block = extract_braced_block(block, m.end())
        dm = re.search(r'default\s*=\s*\{', hb_block)
        if dm:
            db = extract_braced_block(hb_block, dm.end())
            quests = parse_q_from_text(db)
            if quests:
                char["quests"] = quests

    m = re.search(r'questGroups\s*=\s*\{', block)
    if m:
        qg_block = extract_braced_block(block, m.end())
        groups = []
        for gm in re.finditer(r'\{\s*theme\s*=\s*"([^"]+)",\s*count\s*=\s*(\d+)\s*\}', qg_block):
            groups.append({"theme": gm.group(1), "count": int(gm.group(2))})
        if groups:
            char["questGroups"] = groups

    m = re.search(r'^\s*companion\s*=\s*E\("([^"]+)",\s*(\d+)\)', block, re.MULTILINE)
    if m:
        char["companion"] = {"desc": m.group(1), "level": int(m.group(2))}

    m = re.search(r'^\s*pet\s*=\s*E\("([^"]+)",\s*(\d+)\)', block, re.MULTILINE)
    if m:
        char["pet"] = {"desc": m.group(1), "level": int(m.group(2))}

    m = re.search(r'^\s*mount\s*=\s*E\("([^"]+)",\s*(\d+)\)', block, re.MULTILINE)
    if m:
        char["mount"] = {"desc": m.group(1), "level": int(m.group(2))}

    return char


def parse_e_field(block, field_name):
    entries = []
    m = re.search(rf'^\s*{field_name}\s*=\s*\{{', block, re.MULTILINE)
    if not m:
        return entries
    field_text = extract_braced_block(block, m.end())
    for em in re.finditer(r'E\("((?:[^"\\]|\\.)*)",\s*(\d+)(?:,\s*(\d+))?\)', field_text):
        entry = {
            "desc": em.group(1).replace("\\'", "'").replace('\\"', '"'),
            "level": int(em.group(2)),
        }
        if em.group(3):
            entry["endLevel"] = int(em.group(3))
        entries.append(entry)
    return entries


def parse_q_field(block, field_name):
    entries = []
    m = re.search(rf'^\s*{field_name}\s*=\s*\{{', block, re.MULTILINE)
    if not m:
        return entries
    line_start = block.rfind('\n', 0, m.start()) + 1
    line = block[line_start:m.end()]
    if 'questsBy' in line:
        return entries
    field_text = extract_braced_block(block, m.end())
    return parse_q_from_text(field_text)


# ── HTML helpers ──

def esc(s):
    return html.escape(str(s), quote=True)

def make_slug(name):
    return name.lower().replace(" ", "-").replace("'", "")

def make_initials(name):
    parts = name.split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return name[:2].upper()

def make_wiki_url(name):
    return "https://warcraft.wiki.gg/wiki/" + name.replace(" ", "_")

def title_case(s):
    return s[0].upper() + s[1:].lower() if s else s

def render_level(entry):
    level = entry.get("level", 1)
    end = entry.get("endLevel")
    if end:
        return f"Lv {level}&ndash;{end}"
    return f"Lv {level}"


def render_build_details(char, lore, talents_db, challenge_descs):
    """Render detail sections for a single build."""
    wow_class = char["class"]
    name = char["name"]
    parts = []

    # Meta info
    sf = char.get("selfFound", True)
    if sf is True:
        sf_display = "Yes"
    elif sf is False:
        sf_display = "No"
    else:
        sf_display = str(sf)

    meta = [f'<span class="ml">Spec:</span> {esc(char.get("spec", ""))}']
    race = char.get("race", "Any race")
    meta.append(f'<span class="ml">Race:</span> {esc(race) if race != "Any race" else "Any"}')
    gender = char.get("gender", "Any gender")
    if gender != "Any gender":
        meta.append(f'<span class="ml">Gender:</span> {esc(gender)}')
    meta.append(f'<span class="ml">Self-Found:</span> {esc(sf_display)}')
    gameplay = char.get("gameplay")
    if gameplay:
        meta.append(f'<span class="ml">Gameplay:</span> {esc(gameplay)}')
    parts.append(f'<div class="meta">{" &middot; ".join(meta)}</div>')

    # Lore
    lore_text = lore.get(name, "")
    if lore_text:
        sentences = lore_text.split(". ")
        summary = ". ".join(sentences[:3])
        if not summary.endswith("."):
            summary += "."
        parts.append(f'<div class="lore"><p>{esc(summary)}</p></div>')

    # Professions
    if char.get("professions"):
        items = "".join(f"<li>{esc(p)}</li>" for p in char["professions"])
        parts.append(f'<div class="rs"><h4>Professions (Required)</h4><ul>{items}</ul></div>')

    rec = char.get("recommendedProfession")
    if rec:
        parts.append(f'<div class="rs"><h4>Recommended Profession</h4><p><strong>{esc(rec["name"])}</strong> &mdash; {esc(rec["reason"])}</p></div>')

    # Challenges
    if char.get("challenges"):
        rows = ""
        for c in char["challenges"]:
            desc_text = challenge_descs.get(c["desc"], c["desc"])
            rows += f'<tr><td><strong>{esc(c["desc"])}</strong></td><td>{render_level(c)}</td><td>{esc(desc_text)}</td></tr>'
        parts.append(f'<div class="rs"><h4>Challenge Rules</h4><table class="rt"><tr><th>Challenge</th><th>Level</th><th>Description</th></tr>{rows}</table></div>')

    # Equipment
    if char.get("equipment"):
        rows = ""
        for e in char["equipment"]:
            rows += f'<tr><td>{esc(e["desc"])}</td><td>{render_level(e)}</td></tr>'
        parts.append(f'<div class="rs"><h4>Equipment Requirements</h4><table class="rt"><tr><th>Requirement</th><th>Level</th></tr>{rows}</table></div>')

    # Talents (lookup by CLASS_Spec key)
    talent_key = f'{wow_class}_{char.get("spec", "")}'
    talent_data = talents_db.get(talent_key)
    if talent_data and talent_data["entries"]:
        trees = TALENT_TREES.get(wow_class, {})
        rows = ""
        for t in talent_data["entries"]:
            tree_name = trees.get(t["tab"], f"Tree {t['tab']}")
            rows += f'<tr><td>{esc(t["name"])}</td><td>{esc(tree_name)}</td><td>{t["rank"]}</td><td>Lv {t["level"]}</td></tr>'
        roles_html = ""
        if talent_data.get("roles"):
            roles_html = f' <span class="qt">({esc(talent_data["roles"])})</span>'
        parts.append(f'<div class="rs"><h4>Talent Requirements{roles_html}</h4><table class="rt"><tr><th>Talent</th><th>Tree</th><th>Rank</th><th>By Level</th></tr>{rows}</table></div>')

    # Quests
    quests = char.get("quests", [])
    quest_theme = char.get("questTheme", "")
    quest_groups = char.get("questGroups")
    has_faction_quests = bool(char.get("questsByFaction"))

    if has_faction_quests and not quests:
        for faction in ["Alliance", "Horde"]:
            fq = char["questsByFaction"].get(faction, [])
            if fq:
                rows = "".join(f'<tr><td>{esc(q["name"])}</td><td>Lv {q["level"]}</td></tr>' for q in fq)
                suffix = " (A)" if faction == "Alliance" else " (H)"
                theme = f'{quest_theme}{suffix}' if quest_theme else faction
                parts.append(f'<div class="rs"><h4>Quest Milestones <span class="qt">({esc(theme)})</span></h4><table class="rt"><tr><th>Quest</th><th>By Level</th></tr>{rows}</table></div>')
    elif quests and quest_groups:
        rows = ""
        offset = 0
        for qg in quest_groups:
            theme = qg["theme"]
            count = qg["count"]
            group_quests = quests[offset:offset + count]
            if group_quests:
                rows += f'<tr><td colspan="2" style="color:var(--dim);font-style:italic;border-bottom:1px solid var(--brd);padding-top:8px"><strong>{esc(theme)}</strong></td></tr>'
                rows += "".join(f'<tr><td>{esc(q["name"])}</td><td>Lv {q["level"]}</td></tr>' for q in group_quests)
            offset += count
        parts.append(f'<div class="rs"><h4>Quest Milestones</h4><table class="rt"><tr><th>Quest</th><th>By Level</th></tr>{rows}</table></div>')
    elif quests:
        rows = "".join(f'<tr><td>{esc(q["name"])}</td><td>Lv {q["level"]}</td></tr>' for q in quests)
        theme_html = f' <span class="qt">({esc(quest_theme)})</span>' if quest_theme else ""
        parts.append(f'<div class="rs"><h4>Quest Milestones{theme_html}</h4><table class="rt"><tr><th>Quest</th><th>By Level</th></tr>{rows}</table></div>')

    # Companion / Pet / Mount
    cpm = []
    if char.get("companion"):
        c = char["companion"]
        cpm.append(f'<li><strong>Companion:</strong> {esc(c["desc"])} (Lv {c["level"]})</li>')
    if char.get("pet"):
        p = char["pet"]
        cpm.append(f'<li><strong>Hunter Pet:</strong> {esc(p["desc"])} (Lv {p["level"]})</li>')
    if char.get("mount"):
        mt = char["mount"]
        cpm.append(f'<li><strong>Mount:</strong> {esc(mt["desc"])} (Lv {mt["level"]})</li>')
    if cpm:
        parts.append(f'<div class="rs"><h4>Companion / Pet / Mount</h4><ul>{"".join(cpm)}</ul></div>')

    return "".join(parts)


def generate_html(characters, lore, talents, challenge_descs):
    """Generate flat-grid HTML grouped by sphere."""

    # Group characters by display name → list of builds
    name_builds = defaultdict(list)
    for key, char in characters.items():
        name_builds[char["name"]].append(char)

    # Sort builds within each name by class
    class_order = ["WARRIOR", "PALADIN", "HUNTER", "ROGUE", "PRIEST", "SHAMAN", "MAGE", "WARLOCK", "DRUID"]
    for name in name_builds:
        name_builds[name].sort(key=lambda c: class_order.index(c["class"]) if c["class"] in class_order else 99)

    total_names = len(name_builds)
    total_builds = sum(len(b) for b in name_builds.values())

    # Group by sphere
    sphere_groups = defaultdict(list)
    for name in name_builds:
        sphere = CLASS_SPHERE.get(name, "reality")
        sphere_groups[sphere].append(name)
    for sphere in sphere_groups:
        sphere_groups[sphere].sort()

    # Race/class filter buttons
    import json
    race_btns = []
    for r in RACE_ORDER:
        faction = RACE_FACTION[r]
        fc = "#3399ff" if faction == "alliance" else "#ff4444"
        race_btns.append(f'<button class="filter-btn race-btn" data-race="{r.lower()}" style="--fc:{fc}" onclick="selectRace(\'{r.lower()}\')">{r}</button>')
    race_btns_html = "\n    ".join(race_btns)

    class_btns = []
    for c in CLASS_DISPLAY_ORDER:
        cc = CLASS_COLORS[c]
        class_btns.append(f'<button class="filter-btn class-btn" data-class="{c.lower()}" style="--fc:{cc}" onclick="selectClass(\'{c.lower()}\')">{title_case(c)}</button>')
    class_btns_html = "\n    ".join(class_btns)

    # Race→classes and class→races JSON for JS (cross-greying)
    race_classes_json = json.dumps({r.lower(): [c.lower() for c in classes] for r, classes in RACE_CLASSES.items()})
    # Build reverse: class → which races can play it
    class_races = {}
    for race, classes in RACE_CLASSES.items():
        for cls in classes:
            class_races.setdefault(cls.lower(), []).append(race.lower())
    class_races_json = json.dumps(class_races)

    # Build grid cards
    grid_cards = []
    for sphere in SPHERE_ORDER:
        names = sphere_groups.get(sphere, [])
        color = SPHERE_COLORS[sphere]
        for name in names:
            slug = make_slug(name)
            builds = name_builds[name]
            portrait = PORTRAIT_MAP.get(name)
            initials = make_initials(name)
            build_count = len(builds)
            classes = [title_case(b["class"]) for b in builds]
            classes_str = " / ".join(classes)
            # Collect all races and base classes across all builds
            all_races = set()
            all_classes = set()
            for b in builds:
                all_classes.add(b["class"])
                for r in b.get("races", []):
                    all_races.add(r)
            races_data = ",".join(sorted(all_races)).lower()
            classes_data = ",".join(sorted(all_classes)).lower()

            if portrait:
                img_html = f'<img src="Icons/{esc(portrait)}" alt="{esc(name)}" class="grid-img" loading="lazy">'
                fb_style = 'display:none'
            else:
                img_html = ''
                fb_style = f'background:{color}22;border-color:{color}'

            badge_html = ""
            if build_count > 1:
                badge_html = f'<span class="build-badge">{build_count}</span>'

            grid_cards.append(f'''<div class="grid-card" data-sphere="{sphere}" data-name="{esc(name.lower())}" data-classes="{esc(classes_str.lower())}" data-races="{esc(races_data)}" data-baseclasses="{esc(classes_data)}" id="{slug}" onclick="toggleCard(this)">
  <div class="grid-portrait">
    {img_html}
    <div class="grid-fb" style="{fb_style}"><span style="color:{color}">{initials}</span></div>
    {badge_html}
  </div>
  <div class="grid-name" style="color:{color}">{esc(name)}</div>
  <div class="grid-classes">{esc(classes_str)}</div>
</div>''')

    # Build detail panels (hidden, shown on click)
    detail_panels = []
    for sphere in SPHERE_ORDER:
        names = sphere_groups.get(sphere, [])
        color = SPHERE_COLORS[sphere]
        for name in names:
            slug = make_slug(name)
            builds = name_builds[name]
            wiki_url = make_wiki_url(name)

            if len(builds) == 1:
                # Single build — show details directly
                build = builds[0]
                details = render_build_details(build, lore, talents, challenge_descs)
                header = f'{esc(name)} <span class="detail-class">({title_case(build["class"])})</span>'
                detail_panels.append(f'''<div class="detail-panel" id="detail-{slug}" style="--accent:{color}">
  <div class="detail-header">
    <h3 style="color:{color}">{header}</h3>
    <a href="{esc(wiki_url)}" target="_blank" rel="noopener" class="wiki-link" style="color:{color}">Wiki &#128214;</a>
  </div>
  {details}
</div>''')
            else:
                # Multi-build — tabs
                tabs_html = []
                panels_html = []
                for i, build in enumerate(builds):
                    cls = title_case(build["class"])
                    active = " active" if i == 0 else ""
                    tabs_html.append(f'<button class="build-tab{active}" onclick="switchBuildTab(this, \'{slug}\', {i})">{cls}</button>')
                    details = render_build_details(build, lore, talents, challenge_descs)
                    display = "" if i == 0 else "display:none;"
                    panels_html.append(f'<div class="build-panel" data-build="{slug}-{i}" style="{display}">{details}</div>')

                detail_panels.append(f'''<div class="detail-panel" id="detail-{slug}" style="--accent:{color}">
  <div class="detail-header">
    <h3 style="color:{color}">{esc(name)}</h3>
    <a href="{esc(wiki_url)}" target="_blank" rel="noopener" class="wiki-link" style="color:{color}">Wiki &#128214;</a>
  </div>
  <div class="build-tabs">{"".join(tabs_html)}</div>
  {"".join(panels_html)}
</div>''')

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Classic Classes Enhanced — Wiki</title>
<link rel="icon" type="image/png" href="cce_logo.png">
<style>
:root{{--bg:#1a1a2e;--bg2:#16213e;--bg3:#0f3460;--text:#e0e0e0;--dim:#999;--gold:#ffd700;--brd:#2a2a4a}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',system-ui,-apple-system,sans-serif;background:var(--bg);color:var(--text);line-height:1.6}}
a{{color:var(--gold);text-decoration:none}}a:hover{{text-decoration:underline}}

/* Hero */
.hero{{text-align:center;padding:60px 20px 40px;background:linear-gradient(180deg,var(--bg3),var(--bg));border-bottom:1px solid var(--brd)}}
.hero h1{{font-size:2.5rem;color:var(--gold);margin-bottom:12px;text-shadow:0 0 20px rgba(255,215,0,.3)}}
.hero .sub{{font-size:1.15rem;color:var(--dim);max-width:700px;margin:0 auto 24px}}
.badge{{display:inline-block;background:var(--bg3);border:1px solid var(--gold);color:var(--gold);padding:6px 16px;border-radius:20px;font-size:.9rem;margin:4px}}

/* About */
.about{{max-width:1100px;margin:40px auto;padding:0 20px}}
.ag{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px;margin-top:20px}}
.ac{{background:var(--bg2);border:1px solid var(--brd);border-radius:8px;padding:20px}}
.ac h3{{color:var(--gold);font-size:1rem;margin-bottom:8px}}.ac p{{font-size:.9rem;color:var(--dim)}}

/* Race / Class filters */
.filter-wrap{{max-width:1100px;margin:20px auto 0;padding:0 20px}}
.filter-row{{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:6px;margin-bottom:8px}}
.filter-label{{font-size:.8rem;font-weight:700;color:var(--dim);text-transform:uppercase;letter-spacing:.5px;margin-right:4px;min-width:40px}}
.filter-btn{{padding:6px 14px;background:var(--bg2);border:1px solid var(--brd);border-radius:6px;font-size:.82rem;font-weight:600;color:var(--fc,var(--text));cursor:pointer;transition:all .2s}}
.filter-btn:hover{{background:var(--bg3);border-color:var(--fc,#555)}}
.filter-btn.active{{background:var(--bg3);border-color:var(--fc,var(--gold));box-shadow:0 0 6px rgba(255,255,255,.1)}}
.filter-btn.greyed{{opacity:.3;pointer-events:none}}

/* Search */
.sb{{max-width:1100px;margin:20px auto;padding:0 20px}}
.sb input{{width:100%;padding:12px 16px;background:var(--bg2);border:1px solid var(--brd);border-radius:8px;color:var(--text);font-size:1rem;outline:none}}
.sb input:focus{{border-color:var(--gold)}}.sb input::placeholder{{color:var(--dim)}}

/* Grid */
.grid-wrap{{max-width:1100px;margin:20px auto;padding:0 20px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:16px}}
.grid-card{{background:var(--bg2);border:1px solid var(--brd);border-radius:10px;padding:12px;text-align:center;cursor:pointer;transition:all .2s;position:relative}}
.grid-card:hover{{border-color:#555;transform:translateY(-2px)}}
.grid-card.active{{border-color:var(--gold);background:var(--bg3)}}
.grid-portrait{{width:90px;height:90px;margin:0 auto 8px;position:relative}}
.grid-img{{width:90px;height:90px;border-radius:50%;object-fit:cover}}
.grid-fb{{width:90px;height:90px;border-radius:50%;display:flex;align-items:center;justify-content:center;border:2px solid}}
.grid-fb span{{font-size:1.2rem;font-weight:800;letter-spacing:1px}}
.build-badge{{position:absolute;top:-2px;right:-2px;background:var(--bg3);border:1px solid var(--brd);color:var(--gold);font-size:.7rem;font-weight:700;width:20px;height:20px;border-radius:50%;display:flex;align-items:center;justify-content:center}}
.grid-name{{font-size:.9rem;font-weight:600;line-height:1.2}}
.grid-classes{{font-size:.75rem;color:var(--dim);margin-top:2px}}

/* Detail panel (inserted after grid) */
.detail-wrap{{max-width:1100px;margin:0 auto;padding:0 20px}}
.detail-panel{{display:none;background:var(--bg2);border:1px solid var(--brd);border-radius:10px;padding:24px;margin:12px 0 24px;animation:fadeIn .2s}}
.detail-panel.visible{{display:block}}
@keyframes fadeIn{{from{{opacity:0;transform:translateY(-8px)}}to{{opacity:1;transform:translateY(0)}}}}
.detail-header{{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid var(--brd)}}
.detail-header h3{{font-size:1.3rem}}
.detail-class{{font-size:.9rem;font-weight:normal;opacity:.7}}
.wiki-link{{font-size:.85rem;font-weight:600}}

/* Build tabs */
.build-tabs{{display:flex;gap:6px;margin-bottom:16px}}
.build-tab{{padding:6px 16px;background:var(--bg);border:1px solid var(--brd);border-radius:6px;color:var(--dim);font-size:.85rem;font-weight:600;cursor:pointer;transition:all .2s}}
.build-tab:hover{{color:var(--text);border-color:#555}}
.build-tab.active{{color:var(--accent,var(--gold));border-color:var(--accent,var(--gold));background:var(--bg3)}}

/* Shared detail styles */
.meta{{font-size:.82rem;color:var(--dim);margin-bottom:12px}}.ml{{color:var(--text);font-weight:600}}
.lore{{background:rgba(255,215,0,.05);border-left:3px solid var(--gold);padding:12px 16px;margin-bottom:16px;border-radius:0 6px 6px 0}}
.lore p{{font-style:italic;font-size:.9rem;color:var(--dim)}}
.rs{{margin-bottom:16px}}.rs h4{{color:var(--gold);font-size:.9rem;text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px}}
.rs ul{{list-style:none;padding:0}}.rs ul li{{padding:4px 0;font-size:.9rem;border-bottom:1px solid rgba(255,255,255,.05)}}.rs ul li:last-child{{border-bottom:none}}
.qt{{font-weight:normal;color:var(--dim);font-size:.85rem}}
.rt{{width:100%;border-collapse:collapse;font-size:.88rem}}
.rt th{{text-align:left;color:var(--dim);font-weight:600;padding:6px 8px;border-bottom:1px solid var(--brd);font-size:.8rem;text-transform:uppercase;letter-spacing:.3px}}
.rt td{{padding:6px 8px;border-bottom:1px solid rgba(255,255,255,.04)}}.rt tr:last-child td{{border-bottom:none}}

footer{{text-align:center;padding:40px 20px;color:var(--dim);font-size:.85rem;border-top:1px solid var(--brd);margin-top:60px}}

@media(max-width:600px){{
  .hero h1{{font-size:1.8rem}}
  .grid{{grid-template-columns:repeat(auto-fill,minmax(100px,1fr));gap:10px}}
  .grid-portrait,.grid-img,.grid-fb{{width:70px;height:70px}}
  .grid-name{{font-size:.8rem}}
  .detail-panel{{padding:16px}}
  .rt{{font-size:.82rem}}
}}
</style>
</head>
<body>
<div class="hero">
  <h1>Classic Classes Enhanced</h1>
  <p class="sub">{total_names} character archetypes across {total_builds} builds for WoW Classic. Pick an enhanced class and the addon tracks your challenge rules, gear restrictions, quest milestones, and talent requirements as you level.</p>
  <span class="badge">v0.8.6</span>
  <span class="badge">WoW Classic Era</span>
  <span class="badge">{total_names} Enhanced Classes</span>
  <span class="badge">{total_builds} Builds</span>
</div>
<div class="about"><div class="ag">
  <div class="ac"><h3>Real-Time Tracking</h3><p>The addon monitors equipment, talents, quests, challenges, and more in real time. Violations are flagged instantly with alerts.</p></div>
  <div class="ac"><h3>Requirements Panel</h3><p>A persistent, draggable checklist: green checkmarks for met rules, red crosses for violations, grey for level-locked requirements. Access via <code>/cce panel</code>.</p></div>
  <div class="ac"><h3>Auto-Detection</h3><p>Your enhanced class is determined by race, gender, and class. The addon detects it on login. Use <code>/cce pick</code> to choose manually.</p></div>
  <div class="ac"><h3>Installation</h3><p>Drop the <code>ClassicClassesEnhanced</code> folder into your <code>Interface/AddOns</code> directory. Works with Classic Era (Interface 11507).</p></div>
</div></div>
<div class="filter-wrap">
  <div class="filter-row" id="race-row">
    <span class="filter-label">Race</span>
    {race_btns_html}
  </div>
  <div class="filter-row" id="class-row">
    <span class="filter-label">Class</span>
    {class_btns_html}
  </div>
</div>
<div class="sb"><input type="text" id="si" placeholder="Search by name, class, or keyword..." oninput="applyFilters()"></div>
<div class="grid-wrap"><div class="grid" id="card-grid">
{chr(10).join(grid_cards)}
</div></div>
<div class="detail-wrap" id="detail-container">
{chr(10).join(detail_panels)}
</div>
<footer>
  <p>Classic Classes Enhanced by <strong>Beba</strong></p>
  <p><a href="https://buymeacoffee.com/berentbaris">Buy Me a Coffee</a></p>
</footer>
<script>
const RACE_CLASSES = {race_classes_json};
const CLASS_RACES = {class_races_json};
let activeRace = null;
let activeClass = null;
let activeCard = null;

function refreshFilterStates() {{
  // Grey out class buttons incompatible with selected race
  document.querySelectorAll('.class-btn').forEach(b => {{
    const cls = b.dataset.class;
    let grey = false;
    if (activeRace) {{
      const valid = RACE_CLASSES[activeRace] || [];
      if (!valid.includes(cls)) grey = true;
    }}
    if (grey && b.classList.contains('active')) {{
      b.classList.remove('active');
      activeClass = null;
    }}
    b.classList.toggle('greyed', grey);
  }});
  // Grey out race buttons incompatible with selected class
  document.querySelectorAll('.race-btn').forEach(b => {{
    const race = b.dataset.race;
    let grey = false;
    if (activeClass) {{
      const valid = CLASS_RACES[activeClass] || [];
      if (!valid.includes(race)) grey = true;
    }}
    if (grey && b.classList.contains('active')) {{
      b.classList.remove('active');
      activeRace = null;
    }}
    b.classList.toggle('greyed', grey);
  }});
}}

function selectRace(race) {{
  if (activeRace === race) {{
    activeRace = null;
    document.querySelectorAll('.race-btn').forEach(b => b.classList.remove('active'));
  }} else {{
    activeRace = race;
    document.querySelectorAll('.race-btn').forEach(b => {{
      b.classList.toggle('active', b.dataset.race === race);
    }});
  }}
  refreshFilterStates();
  closeDetail();
  applyFilters();
}}

function selectClass(cls) {{
  if (activeClass === cls) {{
    activeClass = null;
    document.querySelectorAll('.class-btn').forEach(b => b.classList.remove('active'));
  }} else {{
    activeClass = cls;
    document.querySelectorAll('.class-btn').forEach(b => {{
      b.classList.toggle('active', b.dataset.class === cls);
    }});
  }}
  refreshFilterStates();
  closeDetail();
  applyFilters();
}}

function applyFilters() {{
  const q = document.getElementById('si').value.toLowerCase();
  document.querySelectorAll('.grid-card').forEach(c => {{
    const textOK = !q || c.dataset.name.includes(q) || c.dataset.classes.includes(q);
    const races = c.dataset.races ? c.dataset.races.split(',') : [];
    const classes = c.dataset.baseclasses ? c.dataset.baseclasses.split(',') : [];
    const raceOK = !activeRace || races.includes(activeRace);
    const classOK = !activeClass || classes.includes(activeClass);
    c.style.display = (textOK && raceOK && classOK) ? '' : 'none';
  }});
}}

function closeDetail() {{
  document.querySelectorAll('.detail-panel.visible').forEach(p => p.classList.remove('visible'));
  document.querySelectorAll('.grid-card.active').forEach(c => c.classList.remove('active'));
  activeCard = null;
}}

function toggleCard(card) {{
  const slug = card.id;
  const panel = document.getElementById('detail-' + slug);
  if (!panel) return;
  if (activeCard === card) {{ closeDetail(); return; }}
  closeDetail();
  activeCard = card;
  card.classList.add('active');
  panel.classList.add('visible');
  panel.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
}}

function switchBuildTab(btn, slug, idx) {{
  const panel = document.getElementById('detail-' + slug);
  if (!panel) return;
  panel.querySelectorAll('.build-tab').forEach(t => t.classList.remove('active'));
  btn.classList.add('active');
  panel.querySelectorAll('.build-panel').forEach((p, i) => {{
    p.style.display = (i === idx) ? '' : 'none';
  }});
}}

if (window.location.hash) {{
  const el = document.querySelector(window.location.hash);
  if (el && el.classList.contains('grid-card')) {{
    setTimeout(() => {{ toggleCard(el); el.scrollIntoView({{ behavior: 'smooth', block: 'start' }}); }}, 200);
  }}
}}
</script></body>
</html>'''


def main():
    char_lua = read_file(os.path.join(LUA_DIR, "CharacterData.lua"))
    lore_lua = read_file(os.path.join(LUA_DIR, "LoreData.lua"))
    talent_lua = read_file(os.path.join(LUA_DIR, "TalentRequirements.lua"))

    lore = parse_lore_data(lore_lua)
    talents = parse_talent_requirements(talent_lua)
    characters, challenge_descs = parse_character_data(char_lua)

    # Group by display name
    name_builds = defaultdict(list)
    for key, char in characters.items():
        name_builds[char["name"]].append(char)

    print(f"Parsed {len(characters)} builds across {len(name_builds)} enhanced classes")
    print(f"Parsed {len(lore)} lore entries")
    print(f"Parsed {len(talents)} talent spec entries")
    print(f"Challenge descriptions: {len(challenge_descs)}")

    # Check sphere coverage
    for name in sorted(name_builds):
        sphere = CLASS_SPHERE.get(name, "???")
        builds = [b["class"] for b in name_builds[name]]
        print(f"  {name}: {sphere} — {builds}")

    html_output = generate_html(characters, lore, talents, challenge_descs)

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_output)

    print(f"\nWrote {len(html_output)} bytes to {OUT_FILE}")


if __name__ == "__main__":
    main()
