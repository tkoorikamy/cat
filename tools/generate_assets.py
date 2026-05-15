from pathlib import Path
import argparse
from PIL import Image, ImageDraw

ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def cat_base(eye="open", paw="down", toy=False, sleep=False, tail=0):
    img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    body = (235, 155, 90, 255)
    ear = (215, 130, 75, 255)
    d.ellipse((40, 80, 220, 220), fill=body)
    d.ellipse((78, 36, 186, 150), fill=body)
    d.polygon([(85, 50), (105, 10), (125, 58)], fill=ear)
    d.polygon([(140, 58), (160, 10), (180, 50)], fill=ear)
    if sleep:
        d.arc((95, 82, 118, 100), 180, 360, fill=(30, 30, 30), width=3)
        d.arc((136, 82, 159, 100), 180, 360, fill=(30, 30, 30), width=3)
    elif eye == "blink":
        d.line((96, 92, 116, 92), fill=(20, 20, 20), width=3)
        d.line((138, 92, 158, 92), fill=(20, 20, 20), width=3)
    else:
        d.ellipse((96, 88, 116, 108), fill=(25, 25, 25))
        d.ellipse((138, 88, 158, 108), fill=(25, 25, 25))
    d.polygon([(126, 112), (119, 120), (133, 120)], fill=(255, 150, 160))
    d.arc((108, 120, 144, 142), 200, 340, fill=(40, 40, 40), width=2)
    y = 180 if paw == "down" else 170
    d.rounded_rectangle((95, y, 120, y + 30), radius=10, fill=(250, 170, 120))
    d.rounded_rectangle((130, y - (8 if paw == 'up' else 0), 155, y + 30 - (8 if paw == 'up' else 0)), radius=10, fill=(250, 170, 120))
    d.rounded_rectangle((48, 190, 200, 225), radius=8, fill=(70, 70, 78, 230))
    for i in range(6):
        d.rectangle((55 + i * 23, 196, 70 + i * 23, 214), fill=(90, 90, 100, 255))
    d.arc((20 + tail, 110, 70 + tail, 220), 260, 80, fill=body, width=16)
    if toy:
        d.ellipse((184, 165, 212, 185), fill=(165, 165, 165, 255))
        d.line((198, 165, 220, 145), fill=(120, 120, 120, 255), width=2)
    return img


def save_set(make_ico: bool = False):
    cat_base(eye="open", paw="down", tail=0).save(ASSETS_DIR / "cat_idle_0.png")
    cat_base(eye="blink", paw="down", tail=4).save(ASSETS_DIR / "cat_idle_1.png")
    cat_base(eye="open", paw="down", tail=8).save(ASSETS_DIR / "cat_idle_2.png")

    cat_base(eye="open", paw="up", tail=2).save(ASSETS_DIR / "cat_typing_0.png")
    cat_base(eye="open", paw="down", tail=6).save(ASSETS_DIR / "cat_typing_1.png")
    cat_base(eye="open", paw="up", tail=10).save(ASSETS_DIR / "cat_typing_2.png")

    cat_base(eye="open", paw="up", toy=True, tail=5).save(ASSETS_DIR / "cat_mouse_0.png")
    cat_base(eye="open", paw="down", toy=True, tail=8).save(ASSETS_DIR / "cat_mouse_1.png")
    cat_base(eye="blink", paw="up", toy=True, tail=11).save(ASSETS_DIR / "cat_mouse_2.png")

    cat_base(sleep=True, paw="down", tail=3).save(ASSETS_DIR / "cat_sleep_0.png")
    cat_base(sleep=True, paw="down", tail=7).save(ASSETS_DIR / "cat_sleep_1.png")

    icon = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    icon.alpha_composite(cat_base().resize((256, 256)))
    tray_png = ASSETS_DIR / "tray_icon.png"
    icon.save(tray_png)
    if make_ico:
        icon.save(ASSETS_DIR / "tray_icon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ico", action="store_true", help="Also generate tray_icon.ico")
    args = parser.parse_args()
    save_set(make_ico=args.ico)
    print("Assets generated in", ASSETS_DIR)
