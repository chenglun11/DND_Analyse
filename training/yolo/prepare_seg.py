import shutil
from pathlib import Path

VOC_ROOT  = Path(r"C:\Users\lchna\Desktop\D20_Room")
OUTPUT    = Path(r"C:\Users\lchna\Desktop\traningdata")
SPLIT     = "train"

IMGS_VOC  = VOC_ROOT / "JPEGImages"
MASKS_VOC = VOC_ROOT / "SegmentationClass"
IMGS_OUT  = OUTPUT / "images" / SPLIT
MASKS_OUT = OUTPUT / "masks" / SPLIT

IMGS_OUT.mkdir(parents=True, exist_ok=True)
MASKS_OUT.mkdir(parents=True, exist_ok=True)

for img in IMGS_VOC.glob("*.*"):
    if img.suffix.lower() in [".png", ".jpg", ".jpeg"]:
        shutil.copy(img, IMGS_OUT / img.name)

for mask in MASKS_VOC.glob("*.*"):
    if mask.suffix.lower() in [".png", ".jpg", ".jpeg"]:
        shutil.copy(mask, MASKS_OUT / mask.name)

print(f"Copied {len(list(IMGS_OUT.iterdir()))} images, {len(list(MASKS_OUT.iterdir()))} masks")
