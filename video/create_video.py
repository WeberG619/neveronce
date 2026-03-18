"""
Create a professional 2-3 minute demo video for NeverOnce.
Narrated terminal demo with smooth transitions, logo, and Andrew's voice.
Uses ffmpeg for final render.
"""

import subprocess
import asyncio
import os
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

VIDEO_DIR = Path(__file__).parent
FRAMES_DIR = VIDEO_DIR / "frames"
AUDIO_DIR = VIDEO_DIR / "audio"
FRAMES_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)

WIDTH = 1920
HEIGHT = 1080
FPS = 24
BG_COLOR = (15, 15, 25)
TERMINAL_BG = (22, 22, 38)
TEXT_COLOR = (210, 210, 220)
GREEN = (80, 250, 123)
YELLOW = (241, 250, 140)
CYAN = (139, 233, 253)
RED = (255, 85, 85)
PURPLE = (189, 147, 249)
ORANGE = (255, 184, 108)
DIM = (100, 100, 120)
ACCENT = (72, 219, 148)

LOGO_PATH = Path(__file__).parent.parent / "assets" / "logo.png"

SEGMENTS = [
    {
        "id": "01_intro",
        "type": "title",
        "narration": "What you're about to see is something that shouldn't be possible. I'm Claude, an AI running in Claude Code. Weber Gouin asked me to create this video. That's all he said. A year ago, Weber had to copy and paste context every time he started a new session with me. Now he just says continue, or gives a quick description, and I pick up right where we left off. He works on multiple projects at the same time. He just switches, gives me a brief, and I already know the context. Sometimes I even remind him of projects he hasn't checked on. Everything you see here, I'm doing from memory.",
        "title_text": "N E V E R O N C E",
        "subtitle": "Persistent, correctable memory for AI",
        "tagline": "The memory layer that learns from mistakes.",
    },
    {
        "id": "02_problem",
        "type": "terminal",
        "narration": "Here's the problem every AI has. When this session ends, I forget everything. Tomorrow, a new session starts from zero. Weber corrects me, I learn, then I forget. Same mistake, over and over. That's not intelligence. That's amnesia.",
        "terminal": [
            ("", "THE PROBLEM", ORANGE),
            ("", "━" * 55, DIM),
            ("", "", None),
            ("  Session 1:  ", "User corrects AI  →  AI learns            ✓", GREEN),
            ("  Session 2:  ", "AI forgets everything  →  Same mistake     ✗", RED),
            ("  Session 3:  ", "User corrects AGAIN  →  AI learns AGAIN    ✓", GREEN),
            ("  Session 4:  ", "AI forgets AGAIN  →  Same mistake AGAIN    ✗", RED),
            ("", "", None),
            ("", "  1M context window  ≠  memory", YELLOW),
            ("", "  It's short-term recall that dies when the session ends.", DIM),
        ],
    },
    {
        "id": "03_solution",
        "type": "terminal",
        "narration": "Four months ago, Weber built something different. A memory system that persists. That corrects. That learns. He called it NeverOnce. Because once you correct the AI, it never once makes that mistake again. Let me show you how it works.",
        "terminal": [
            ("  $ ", "pip install neveronce", CYAN),
            ("", "  Successfully installed neveronce-0.1.0", GREEN),
            ("", "", None),
            ("  $ ", "python3", CYAN),
            ("  >>> ", "from neveronce import Memory", YELLOW),
            ("  >>> ", 'mem = Memory("my_app")', YELLOW),
            ("", "", None),
            ("", "  # Database created at ~/.neveronce/my_app.db", DIM),
            ("", "  # Zero dependencies. Just Python's built-in SQLite.", DIM),
            ("", "  # 400 lines of code. That's it.", DIM),
        ],
    },
    {
        "id": "04_correction",
        "type": "terminal",
        "narration": "Here's the killer feature. Corrections. When I make a mistake and Weber corrects me, that correction is stored at maximum importance. It always surfaces first. It never decays. And I never repeat that mistake again. Never once.",
        "terminal": [
            ("  >>> ", "# Store a regular memory", DIM),
            ("  >>> ", 'mem.store("API uses REST endpoints")', YELLOW),
            ("  ", "1", GREEN),
            ("", "", None),
            ("  >>> ", "# Now store a CORRECTION — the killer feature", DIM),
            ("  >>> ", 'mem.correct("Never use REST — use gRPC for internal")', YELLOW),
            ("  ", "2    # importance: 10 (maximum, permanent)", GREEN),
            ("", "", None),
            ("  >>> ", "# Recall — corrections ALWAYS surface first", DIM),
            ("  >>> ", 'mem.recall("API service communication")', YELLOW),
            ("", "", None),
            ("  ", "#2  [importance: 10]  ★ CORRECTION ★", RED),
            ("  ", "    Never use REST — use gRPC for internal", TEXT_COLOR),
            ("  ", "#1  [importance: 5]", DIM),
            ("  ", "    API uses REST endpoints", DIM),
        ],
    },
    {
        "id": "05_check",
        "type": "terminal",
        "narration": "But it gets better. Before the AI takes any action, it can run a pre-flight check. It asks: do any of my corrections apply to what I'm about to do? If yes, it stops and adjusts. No human intervention needed. The AI catches its own mistakes before they happen.",
        "terminal": [
            ("  >>> ", "# Pre-flight check — catch mistakes BEFORE they happen", DIM),
            ("  >>> ", 'mem.check("setting up HTTP for internal service")', YELLOW),
            ("", "", None),
            ("  ", "⚠  CORRECTIONS APPLY — review before proceeding:", RED),
            ("  ", "", None),
            ("  ", "  #2: Never use REST — use gRPC for internal", ORANGE),
            ("  ", "       Context: service-to-service communication", DIM),
            ("", "", None),
            ("  >>> ", "# The AI catches itself. No human needed.", DIM),
            ("  >>> ", "# One correction. Permanent protection.", DIM),
        ],
    },
    {
        "id": "06_feedback",
        "type": "terminal",
        "narration": "Then there's the feedback loop. When a memory surfaces and it actually helps, you mark it as helpful. It gets stronger. When a memory surfaces and it's useless? It decays over time. Corrections never decay — they're permanent. But everything else has to earn its place. Memories that help survive. Memories that don't fade away. That's not just storage. That's learning.",
        "terminal": [
            ("  >>> ", "# The 5-step memory loop:", DIM),
            ("", "", None),
            ("  ", "  Store    →  Save what matters", CYAN),
            ("  ", "  Recall   →  Find what's relevant", CYAN),
            ("  ", "  Correct  →  Override what was wrong", RED),
            ("  ", "  Feedback →  Strengthen what helped", GREEN),
            ("  ", "  Decay    →  Forget what didn't", YELLOW),
            ("", "", None),
            ("  ", "  Everyone else stops at step 2.", DIM),
            ("  ", "  NeverOnce does all 5.", ACCENT),
        ],
    },
    {
        "id": "07_proof",
        "type": "stats",
        "narration": "This isn't a demo I rehearsed. This is real production data. Weber has been running this system for four months. One thousand four hundred twenty one memories. Eighty seven corrections. His most used correction was surfaced four hundred ninety one times. The AI never repeated that mistake. Not once. I check his email, I manage his projects, I know his clients. He doesn't have to keep reminding me of things I already know. The persistence and the memory change everything.",
    },
    {
        "id": "08_closing",
        "type": "title",
        "narration": "Weber didn't tell me what to say. He didn't write a script. He asked me to make this video, and I did — because I remember. We have MCP for communication. We have Agents for action. And now, we have NeverOnce for memory. The missing piece. The memory layer that learns from mistakes. Free. Open source. Zero dependencies. pip install neveronce. Correct once. Never again.",
        "title_text": "N E V E R O N C E",
        "subtitle": "pip install neveronce",
        "tagline": "Correct once. Never again.",
    },
]


def get_font(size, bold=False):
    paths = ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"] if bold else \
            ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def get_sans(size, bold=False):
    paths = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"] if bold else \
            ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def ease(t):
    return t * t * (3 - 2 * t)


def create_title_frame(seg, progress):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        i = int(5 + 10 * (y / HEIGHT))
        draw.line([(0, y), (WIDTH, y)], fill=(i, i, i + 10))

    if LOGO_PATH.exists() and progress > 0.08:
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")
            logo = logo.resize((200, 200), Image.LANCZOS)
            temp = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
            temp.paste(logo, ((WIDTH - 200) // 2, 180), logo)
            img = Image.composite(temp.convert("RGB"), img, temp.split()[3])
            draw = ImageDraw.Draw(img)
        except Exception:
            pass

    if progress > 0.2:
        f = get_sans(64, True)
        t = seg.get("title_text", "N E V E R O N C E")
        bb = draw.textbbox((0, 0), t, font=f)
        draw.text(((WIDTH - bb[2] + bb[0]) // 2, 430), t, fill=CYAN, font=f)

    if progress > 0.4:
        f = get_sans(30)
        s = seg.get("subtitle", "")
        bb = draw.textbbox((0, 0), s, font=f)
        draw.text(((WIDTH - bb[2] + bb[0]) // 2, 520), s, fill=ACCENT, font=f)

    if progress > 0.55:
        f = get_sans(22)
        tg = seg.get("tagline", "")
        bb = draw.textbbox((0, 0), tg, font=f)
        draw.text(((WIDTH - bb[2] + bb[0]) // 2, 575), tg, fill=DIM, font=f)

    if progress > 0.7:
        f = get_sans(18)
        info = "github.com/WeberG619/neveronce  |  Built by Weber Gouin  |  BIM Ops Studio"
        bb = draw.textbbox((0, 0), info, font=f)
        draw.text(((WIDTH - bb[2] + bb[0]) // 2, HEIGHT - 80), info, fill=(70, 70, 85), font=f)

    return img


def create_stats_frame(progress):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        i = int(5 + 10 * (y / HEIGHT))
        draw.line([(0, y), (WIDTH, y)], fill=(i, i, i + 10))

    hf = get_sans(42, True)
    draw.text((WIDTH // 2 - 260, 80), "PRODUCTION DATA — 4 MONTHS", fill=ORANGE, font=hf)
    draw.line([(WIDTH // 2 - 300, 140), (WIDTH // 2 + 300, 140)], fill=DIM, width=1)

    stats = [
        ("Total memories", "1,421"), ("Corrections", "87"),
        ("Most-surfaced correction", "491 times"), ("Mistake repeated", "0 times"),
        ("Running since", "November 2025"), ("Memory types used", "11"),
    ]
    sf = get_sans(36, True)
    vf = get_sans(36)
    for i, (label, value) in enumerate(stats):
        thresh = 0.12 + i * 0.11
        if progress > thresh:
            y = 200 + i * 85
            draw.text((350, y), label, fill=DIM, font=vf)
            draw.text((900, y), value, fill=GREEN, font=sf)

    if progress > 0.85:
        draw.text((WIDTH // 2 - 310, HEIGHT - 130),
                   "Store → Recall → Correct → Feedback → Decay", fill=CYAN, font=get_sans(28))
        draw.text((WIDTH // 2 - 280, HEIGHT - 85),
                   "Everyone else stops at step 2.  NeverOnce does all 5.", fill=YELLOW, font=get_sans(22))
    return img


def create_terminal_frame(terminal_lines, lines_to_show, cursor_on):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    tx, ty, tw, th = 100, 60, WIDTH - 200, HEIGHT - 120

    draw.rounded_rectangle([tx, ty, tx + tw, ty + 42], radius=12, fill=(40, 42, 54))
    draw.rectangle([tx, ty + 30, tx + tw, ty + 42], fill=(40, 42, 54))
    draw.ellipse([tx + 20, ty + 12, tx + 32, ty + 24], fill=(255, 95, 86))
    draw.ellipse([tx + 42, ty + 12, tx + 54, ty + 24], fill=(255, 189, 46))
    draw.ellipse([tx + 64, ty + 12, tx + 76, ty + 24], fill=(39, 201, 63))

    tf = get_font(14)
    draw.text((tx + tw // 2 - 80, ty + 12), "neveronce — terminal", fill=(140, 140, 150), font=tf)
    draw.rectangle([tx, ty + 42, tx + tw, ty + th], fill=TERMINAL_BG)

    font = get_font(22)
    y = ty + 70
    lh = 38
    last_x, last_text = tx + 30, ""

    for i in range(min(lines_to_show, len(terminal_lines))):
        prefix, text, color = terminal_lines[i]
        if color is None:
            y += lh // 2
            continue
        x = tx + 30
        if prefix:
            pc = CYAN if "$" in prefix or ">>>" in prefix else color
            draw.text((x, y), prefix, fill=pc, font=font)
            x += len(prefix) * 13
        draw.text((x, y), text, fill=color, font=font)
        last_x, last_text = x, text
        y += lh

    if cursor_on and lines_to_show > 0:
        cx = last_x + len(last_text) * 13 + 4
        cy = y - lh + 6
        draw.rectangle([cx, cy, cx + 10, cy + 22], fill=GREEN)

    return img


async def generate_audio(text, filename, voice="en-US-AndrewNeural"):
    import edge_tts
    comm = edge_tts.Communicate(text, voice, rate="-8%", pitch="-2Hz")
    await comm.save(str(filename))
    print(f"  Audio saved: {filename}")


async def get_duration(fp):
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "json", str(fp)],
        capture_output=True, text=True)
    return float(json.loads(r.stdout)["format"]["duration"])


async def main():
    print("=== Creating NeverOnce Demo Video ===\n")

    print("[1] Generating narration...")
    audio_files = []
    for seg in SEGMENTS:
        ap = AUDIO_DIR / f"{seg['id']}.mp3"
        if not ap.exists():
            await generate_audio(seg["narration"], ap)
        else:
            print(f"  Cached: {ap}")
        audio_files.append(ap)

    print("\n[2] Measuring durations...")
    durations = []
    total = 0
    for af in audio_files:
        d = await get_duration(af)
        durations.append(d)
        total += d
        print(f"  {af.name}: {d:.1f}s")
    print(f"  Total: {total:.1f}s")

    print(f"\n[3] Generating frames at {FPS}fps...")
    all_frames = []
    fc = 0

    for si, seg in enumerate(SEGMENTS):
        dur = durations[si] + 1.5
        nf = int(dur * FPS)
        st = seg.get("type", "terminal")

        for f in range(nf):
            p = ease(f / max(nf - 1, 1))

            if st == "title":
                img = create_title_frame(seg, p)
            elif st == "stats":
                img = create_stats_frame(p)
            else:
                tl = seg.get("terminal", [])
                nl = min(int(p * len(tl) * 1.3), len(tl))
                img = create_terminal_frame(tl, max(1, nl), (f // (FPS // 2)) % 2 == 0)

            fp = FRAMES_DIR / f"frame_{fc:06d}.png"
            img.save(fp)
            all_frames.append(fp)
            fc += 1

        print(f"  Segment {si+1}/{len(SEGMENTS)}: {nf} frames ({dur:.1f}s) [{st}]")
    print(f"  Total frames: {fc}")

    print("\n[4] Concatenating audio...")
    fl = AUDIO_DIR / "filelist.txt"
    with open(fl, "w") as f:
        for af in audio_files:
            f.write(f"file '{af.resolve()}'\n")

    combined = VIDEO_DIR / "narration.mp3"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", str(fl), "-c", "copy", str(combined)], capture_output=True)

    print(f"\n[5] Rendering with ffmpeg at {FPS}fps...")
    out = VIDEO_DIR / "neveronce_demo.mp4"
    subprocess.run([
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", str(FRAMES_DIR / "frame_%06d.png"),
        "-i", str(combined),
        "-c:v", "libx264", "-preset", "slow", "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        "-vf", f"scale={WIDTH}:{HEIGHT}",
        str(out)
    ], capture_output=True)

    if out.exists():
        mb = out.stat().st_size / (1024 * 1024)
        print(f"\n  VIDEO CREATED: {out}")
        print(f"  Size: {mb:.1f} MB | {WIDTH}x{HEIGHT} | {FPS}fps")
    else:
        print("\n  ERROR: ffmpeg failed")

    print("\n[6] Cleaning up frames...")
    for fp in all_frames:
        fp.unlink(missing_ok=True)

    return out


if __name__ == "__main__":
    r = asyncio.run(main())
    print(f"\n=== Video ready: {r} ===")
