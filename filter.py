# filter.py
import sys
from pathlib import Path
from PIL import Image
from nudenet import NudeDetector  # lightweight CPU detector

detector = NudeDetector()   # downloads 25 MB model once, then caches

def main(image_path: str):
    img = Image.open(image_path).convert("RGB")   # ensure RGB
    result = detector.detect(image_path)          # list of dicts
    unsafe = any(r["class"] != "safe" and r["score"] > 0.5 for r in result)

    if unsafe:
        print("🔴 NSFW")
    else:
        print("🟢 SAFE")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python filter.py path/to/image.jpg")
        sys.exit(1)
    main(sys.argv[1])