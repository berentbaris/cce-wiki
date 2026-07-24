"""Copy circular icon PNGs from the addon's Icons/ folder to the wiki's icons/ folder."""
import os, shutil

ICONS_SRC = r"C:\Users\beren\Objet\wow_addon\ClassicClassesEnhanced\Icons"
ICONS_DST = r"C:\Users\beren\Objet\cce-wiki\icons"
LOG = r"C:\Users\beren\Objet\cce-wiki\convert_log.txt"

os.makedirs(ICONS_DST, exist_ok=True)
log_lines = []
def log(msg):
    print(msg)
    log_lines.append(msg)

copied = 0
for f in sorted(os.listdir(ICONS_SRC)):
    if not f.lower().endswith(".png"):
        continue
    # Skip per-build icons (e.g. Exemplar_PALADIN.png) — only copy base name icons
    base = f[:-4]
    if "_" in base:
        parts = base.rsplit("_", 1)
        if parts[1] in ("WARRIOR", "ROGUE", "WARLOCK", "DRUID", "HUNTER", "SHAMAN", "PALADIN", "PRIEST", "MAGE"):
            continue
    src_path = os.path.join(ICONS_SRC, f)
    dst_path = os.path.join(ICONS_DST, f)
    shutil.copy2(src_path, dst_path)
    log(f"  OK: {f}")
    copied += 1

log(f"\nDone! {copied} icons copied.")

with open(LOG, "w") as lf:
    lf.write("\n".join(log_lines))
