"""Detect real format of .tga files (they're actually JPEG/PNG) and copy with correct extension."""
import os, shutil

SRC = r"C:\wow_addon\ClassicClassesEnhanced\Backgrounds"
DST = r"C:\cce-wiki\portraits"
LOG = r"C:\cce-wiki\convert_log.txt"

os.makedirs(DST, exist_ok=True)
log_lines = []
def log(msg):
    print(msg)
    log_lines.append(msg)

converted = 0
errors = 0

for f in sorted(os.listdir(SRC)):
    if not f.lower().endswith(".tga"):
        continue
    src_path = os.path.join(SRC, f)
    base = f[:-4]
    try:
        with open(src_path, "rb") as fh:
            header = fh.read(8)

        # Detect real format
        if header[:3] == b'\xff\xd8\xff':
            ext = ".jpg"
            fmt = "JPEG"
        elif header[:4] == b'\x89PNG':
            ext = ".png"
            fmt = "PNG"
        elif header[2:3] in (b'\x02', b'\x0a'):
            ext = ".png"  # real TGA — would need conversion, skip for now
            fmt = "TGA"
            log(f"  SKIP: {f} is actual TGA (would need Pillow)")
            continue
        else:
            log(f"  SKIP: {f} unknown format: {header[:8].hex()}")
            continue

        # Copy with correct web extension — for the wiki we'll use .png for everything
        # JPEGs stay as .jpg, PNGs stay as .png
        dst_path = os.path.join(DST, base + ext)
        shutil.copy2(src_path, dst_path)
        log(f"  OK: {f} -> {base}{ext} ({fmt})")
        converted += 1
    except Exception as e:
        log(f"  FAIL: {f} -> {e}")
        errors += 1

log(f"\nDone! {converted} copied, {errors} errors.")

with open(LOG, "w") as lf:
    lf.write("\n".join(log_lines))
