"""Vertical 9:16 story frame (1080x1920): photo background, Buddha cut-out low on one side, quote above him.
Keeps clear of Instagram's top/bottom UI zones. Usage: python -m buddha_post.make_story bg.jpg "quote||Name" out.jpg [left|right]"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
HERE = Path(__file__).parent
CHAR = Image.open(HERE.parent/"assets/buddha.png").convert("RGBA")
FONT = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
W, H = 1080, 1920

def make(bg_path, quote, out, side="left"):
    quote, _, attribution = quote.partition("||"); quote, attribution = quote.strip(), attribution.strip()
    img = ImageOps.fit(Image.open(bg_path).convert("RGB"), (W, H), Image.LANCZOS).convert("RGBA")
    img = Image.alpha_composite(img, Image.new("RGBA", (W, H), (0, 0, 0, 46)))
    ch_h = int(H*0.40)
    ch = CHAR.resize((int(CHAR.width*ch_h/CHAR.height), ch_h), Image.LANCZOS)
    x = -int(ch.width*0.05) if side == "left" else W-ch.width+int(ch.width*0.05)
    y = H-ch.height-int(H*0.14)  # above the reply bar
    sh = Image.new("RGBA", img.size, (0,0,0,0)); sh.paste((0,0,0,90), (x+8, y+10), ch.split()[3])
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(14)))
    img.alpha_composite(ch, (x, y))
    col_x0, col_w = int(W*0.09), int(W*0.82)
    top, bot = int(H*0.14), int(H*0.54)  # text zone clear of top/bottom UI
    scrim = Image.new("RGBA", img.size, (0,0,0,0)); ImageDraw.Draw(scrim).rectangle((col_x0-30, top, col_x0+col_w+30, bot), fill=(0,0,0,70))
    img = Image.alpha_composite(img, scrim.filter(ImageFilter.GaussianBlur(70)))
    d = ImageDraw.Draw(img)
    for size in range(84, 34, -2):
        f = ImageFont.truetype(FONT, size); lines, cur = [], ""
        for w in quote.split():
            t = (cur+" "+w).strip()
            if d.textlength(t, font=f) <= col_w: cur = t
            else: lines.append(cur); cur = w
        lines.append(cur); lh = int(size*1.22)
        if len(lines)*lh + (lh if attribution else 0) <= bot-top: break
    items = [(l, f, i*lh) for i, l in enumerate(lines)]
    if attribution:
        af = ImageFont.truetype(FONT, max(30, int(size*0.6)))
        items.append(("— " + attribution, af, len(lines)*lh + int(lh*0.2)))
    total = items[-1][2] + lh
    ty = top + (bot-top-total)//2
    shadow = Image.new("RGBA", img.size, (0,0,0,0)); sd = ImageDraw.Draw(shadow)
    for l, fnt, yy in items:
        lx = col_x0+(col_w-d.textlength(l, font=fnt))//2
        sd.text((lx+2, ty+yy+3), l, font=fnt, fill=(0,0,0,200), stroke_width=5, stroke_fill=(0,0,0,150))
    img = Image.alpha_composite(img, shadow.filter(ImageFilter.GaussianBlur(7)))
    d = ImageDraw.Draw(img)
    for l, fnt, yy in items:
        d.text((col_x0+(col_w-d.textlength(l, font=fnt))//2, ty+yy), l, font=fnt, fill=(255,255,255))
    img.convert("RGB").save(out, quality=92)

if __name__ == "__main__":
    a = sys.argv; make(a[1], a[2], a[3], a[4] if len(a) > 4 else "left")
