"""Capture submission screenshots + demo video for Testify."""

from __future__ import annotations

import shutil
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8000"
ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT / "docs" / "screenshots"
VIDEO_DIR = ROOT / "docs" / "demo"
OUT_VIDEO = ROOT / "docs" / "demo" / "testify-demo.webm"

USER = f"demo_{int(time.time())}"
PASSWORD = "DemoPass123!"
EMAIL = f"{USER}@example.com"
SPACE_SLUG = f"acme-{int(time.time()) % 100000}"


def shot(page, name: str) -> None:
    path = SHOTS / f"{name}.png"
    page.screenshot(path=str(path), full_page=True)
    print(f"saved {path.relative_to(ROOT)}")


def main() -> int:
    SHOTS.mkdir(parents=True, exist_ok=True)
    if VIDEO_DIR.exists():
        shutil.rmtree(VIDEO_DIR)
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            record_video_dir=str(VIDEO_DIR),
            record_video_size={"width": 1280, "height": 800},
        )
        page = context.new_page()
        page.set_default_timeout(15000)

        # 1. Landing
        page.goto(f"{BASE}/")
        page.wait_for_load_state("networkidle")
        shot(page, "01-landing")
        time.sleep(0.8)

        # 2. Register
        page.goto(f"{BASE}/accounts/register/")
        page.fill("#id_username", USER)
        page.fill("#id_email", EMAIL)
        page.fill("#id_password1", PASSWORD)
        page.fill("#id_password2", PASSWORD)
        shot(page, "02-register")
        page.locator("main form button[type=submit]").click()
        page.wait_for_url("**/dashboard/**")
        shot(page, "03-dashboard-empty")
        time.sleep(0.6)

        # 3. Create space
        page.goto(f"{BASE}/spaces/new/")
        page.fill("#id_name", "Acme Demo")
        page.fill("#id_slug", SPACE_SLUG)
        page.fill("#id_header_title", "Share your experience with Acme")
        page.fill("#id_message", "Tell us how Acme helped your team ship faster.")
        if not page.locator("#id_collect_ratings").is_checked():
            page.check("#id_collect_ratings")
        page.select_option("#id_theme", "light")
        shot(page, "04-create-space")
        with page.expect_navigation(timeout=20000):
            page.locator("main form button[type=submit]").click()
        if f"/spaces/{SPACE_SLUG}/" not in page.url:
            shot(page, "04-create-space-error")
            raise RuntimeError(f"Space create failed at {page.url}: {page.content()[:800]}")
        shot(page, "05-space-detail")
        time.sleep(0.6)

        # 4. Collect (public, logged out for realism)
        context.clear_cookies()
        page.goto(f"{BASE}/s/{SPACE_SLUG}/")
        page.wait_for_load_state("networkidle")
        shot(page, "06-collect-empty")
        page.fill("#id_name", "Jordan Lee")
        page.fill("#id_email", "jordan@example.com")
        page.fill("#id_body", "Acme cut our deploy time in half. The team loves it.")
        page.locator("input[name=rating][value='5']").check()
        page.check("#id_consent")
        shot(page, "07-collect-filled")
        page.locator("main form button[type=submit]").click()
        page.wait_for_selector("text=Thank you")
        shot(page, "08-thank-you")
        time.sleep(0.8)

        # 5. Login + inbox approve
        page.goto(f"{BASE}/accounts/login/")
        page.fill("#id_username", USER)
        page.fill("#id_password", PASSWORD)
        page.locator("main form button[type=submit]").click()
        page.wait_for_url("**/dashboard/**")
        page.goto(f"{BASE}/spaces/{SPACE_SLUG}/inbox/")
        page.wait_for_selector("text=Jordan Lee")
        shot(page, "09-inbox-pending")
        page.locator("button:has-text('Approve')").click()
        page.wait_for_selector("text=Approved")
        shot(page, "10-inbox-approved")
        time.sleep(0.8)

        # 6. Wall of Love
        page.goto(f"{BASE}/s/{SPACE_SLUG}/wall/")
        page.wait_for_selector("text=Acme cut our deploy time")
        shot(page, "11-wall-of-love")
        time.sleep(1.2)

        video_path = Path(page.video.path())
        context.close()
        browser.close()

        final = OUT_VIDEO
        if final.exists():
            final.unlink()
        shutil.move(str(video_path), str(final))
        print(f"saved {final.relative_to(ROOT)}")

    # Convert webm -> mp4 if ffmpeg available
    mp4 = final.with_suffix(".mp4")
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        import subprocess

        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-i",
                str(final),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                str(mp4),
            ],
            check=False,
            capture_output=True,
        )
        if mp4.exists():
            print(f"saved {mp4.relative_to(ROOT)}")

    index = ROOT / "docs" / "DEMO.md"
    shots_list = "\n".join(
        f"- `{p.relative_to(ROOT).as_posix()}`" for p in sorted(SHOTS.glob("*.png"))
    )
    index.write_text(
        f"""# Demo assets

Generated by `python scripts/capture_demo.py`.

## Recording

- `docs/demo/testify-demo.webm`
- `docs/demo/testify-demo.mp4` (if ffmpeg available)

## Screenshots

{shots_list}

## Flow covered

1. Landing
2. Register
3. Create Space
4. Public collect + thank you
5. Inbox approve
6. Wall of Love
""",
        encoding="utf-8",
    )
    print(f"saved {index.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
