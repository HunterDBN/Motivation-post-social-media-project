"""Carousel slide in Hunter's reference style: plain photo background, Buddha cut-out on the
left, centered white sans-serif quote with soft shadow on the right.
Usage: python -m buddha_post.make_slide bg.jpg "quote" out.jpg [left|right]"""
import sys, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
HERE = Path(__file__).parent
CHAR = Image.open(HERE.parent/"assets/buddha.png").convert("RGBA")
FONT = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
W, H = 1080, 1350  # 4:5, works for Instagram, Facebook and TikTok photo mode

def make(bg_path, quote, out, side="left"):
    quote, _, attribution = quote.partition("||")  # "quote text||Seneca" -> small "- Seneca" line under it
    quote, attribution = quote.strip(), attribution.strip()
    bg = ImageOps.fit(Image.open(bg_path).convert("RGB"), (W, H), Image.LANCZOS)
    img = bg.convert("RGBA")
    img = Image.alpha_composite(img, Image.new("RGBA", (W, H), (0, 0, 0, 46)))  # light dim so white text reads
    ch_h = int(H*0.62)
    ch = CHAR.resize((int(CHAR.width*ch_h/CHAR.height), ch_h), Image.LANCZOS)
    x = -int(ch.width*0.08) if side == "left" else W-ch.width+int(ch.width*0.08)
    y = H-ch.height+int(ch_h*0.04)
    sh = Image.new("RGBA", img.size, (0,0,0,0))
    sh.paste((0,0,0,90), (x+8, y+10), ch.split()[3])
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(14)))
    img.alpha_composite(ch, (x, y))
    # text column on the opposite side
    col_x0 = int(W*0.40) if side == "left" else int(W*0.05)
    col_w = int(W*0.55)
    d = ImageDraw.Draw(img)
    for size in range(64, 28, -2):
        f = ImageFont.truetype(FONT, size)
        lines, cur = [], ""
        for w in quote.split():
            t = (cur+" "+w).strip()
            if d.textlength(t, font=f) <= col_w: cur = t
            else: lines.append(cur); cur = w
        lines.append(cur); lh = int(size*1.22)
        if len(lines)*lh + (lh if attribution else 0) <= H*0.62: break
    if attribution:
        af = ImageFont.truetype(FONT, max(26, int(size*0.62)))
        lines.append(""); alines = [("\u2014 " + attribution, af)]
    else: alines = []
    ty = (H-(len(lines)*lh+int(lh*0.2)*bool(alines)))//2 - int(H*0.03)
    shadow = Image.new("RGBA", img.size, (0,0,0,0)); sd = ImageDraw.Draw(shadow)
    items = [(l, f, ty+i*lh) for i, l in enumerate(lines)]
    for al, afont in alines: items[-1] = (al, afont, ty+(len(lines)-1)*lh+int(lh*0.2))
    for l, fnt, yy in items:
        lx = col_x0+(col_w-d.textlength(l, font=fnt))//2
        sd.text((lx+2, yy+3), l, font=fnt, fill=(0,0,0,200), stroke_width=5, stroke_fill=(0,0,0,150))
    img = Image.alpha_composite(img, shadow.filter(ImageFilter.GaussianBlur(7)))
    d = ImageDraw.Draw(img)
    for l, fnt, yy in items:
        lx = col_x0+(col_w-d.textlength(l, font=fnt))//2
        d.text((lx, yy), l, font=fnt, fill=(255,255,255))
    img.convert("RGB").save(out, quality=92)

if __name__ == "__main__":
    a = sys.argv; make(a[1], a[2], a[3], a[4] if len(a) > 4 else "left")
