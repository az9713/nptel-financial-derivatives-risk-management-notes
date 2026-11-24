"""Acquire local caption evidence; never download video or publish signed URLs."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import gzip
import json
import re
from html import unescape

import requests

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "work" / "acquisition"
PLAYLIST = "https://www.youtube.com/playlist?list=PLLy_2iUCG87CTB2vv9njHaJbmQoa9S5gK"
PRIVATE.mkdir(parents=True, exist_ok=True)
# The public manifest is sufficient to reacquire the public official captions.
# A source-free clone need not contain the ignored original metadata caches.
PUBLISHED = json.loads((ROOT / "source-manifest.json").read_text(encoding="utf-8"))
OLD_RECORDINGS = {r["video_id"]: r for r in PUBLISHED["recordings"]}
if (PRIVATE / "official-outline.json").exists():
    official = json.loads((PRIVATE / "official-outline.json").read_text(encoding="utf-8"))
    LESSONS = {l["youtube_id"]: l for unit in official["units"] for l in unit["lessons"]}
else:
    LESSONS = {
        r["video_id"]: {
            "id": r["lecture_number"], "name": r["teaching_title"],
            "vtt_url": {"English": r["official_caption_url"].split("id=", 1)[1]},
        }
        for r in PUBLISHED["recordings"] if r.get("official_caption_url")
    }


def normalize_json3(raw):
    """Keep actual timed events; join textual fragments, preserving event order."""
    result = []
    for event in raw.get("events", []):
        text = "".join(s.get("utf8", "") for s in event.get("segs", []))
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            result.append({"start": event.get("tStartMs", 0) / 1000,
                           "duration": event.get("dDurationMs", 0) / 1000,
                           "text": text})
    if not result:
        raise ValueError("Empty timed caption JSON")
    return result


def vtt_seconds(value):
    parts = [float(p) for p in value.split(":")]
    return sum(p * 60 ** i for i, p in enumerate(reversed(parts)))


def normalize_vtt(payload):
    text = payload.decode("utf-8-sig").replace("\r\n", "\n")
    result = []
    for match in re.finditer(r"(?m)^([0-9:.]+) --> ([0-9:.]+)[^\n]*\n(.*?)(?=\n\n|\Z)", text, re.S):
        start, end = vtt_seconds(match[1]), vtt_seconds(match[2])
        body = unescape(re.sub(r"<[^>]+>", "", match[3]))
        body = re.sub(r"\s+", " ", body).strip()
        if body:
            result.append({"start": start, "duration": end-start, "text": body})
    if not result:
        raise ValueError("No timed VTT cues")
    return result


def acquisition_entry(item):
    position, entry = item
    vid = entry["id"]
    archive = PRIVATE / f"{position:02d}-{vid}.json.gz"
    title = entry["title"]
    lesson = LESSONS.get(vid)
    number = lesson["id"] if lesson else None
    meta = dict(position=position, playlist_position=position, video_id=vid,
                title=title, teaching_title=lesson["name"].strip() if lesson else title,
                duration=entry.get("duration"), duration_seconds=entry.get("duration"),
                url=f"https://www.youtube.com/watch?v={vid}",
                lecture_number=number, role="introduction" if position == 1 else "lecture")
    if lesson:
        meta["title_provenance"] = "Official NPTEL course outline, exact video-ID match"
        meta["official_caption_url"] = "https://drive.google.com/uc?export=download&id=" + lesson["vtt_url"]["English"]
    if archive.exists():
        data = json.loads(gzip.decompress(archive.read_bytes()))
        method = data.get("acquisition_method", "youtube_transcript_api")
    else:
        try:
            if not lesson:
                raise ValueError("No official caption mapping for this entry")
            raw_path = PRIVATE / f"{position:02d}-{vid}.official.vtt.gz"
            if raw_path.exists():
                payload = gzip.decompress(raw_path.read_bytes())
            else:
                response = requests.get(meta["official_caption_url"], timeout=35)
                response.raise_for_status()
                payload = response.content
                if not payload.lstrip().startswith(b"WEBVTT"):
                    raise ValueError("Official VTT endpoint returned a different format")
                raw_path.write_bytes(gzip.compress(payload, mtime=0))
            lang, track_name, generated = "en", "NPTEL official English VTT", False
            method = "Public official NPTEL course-outline caption link"
            raw_digest = sha256(payload).hexdigest()
            data = {"video_id": vid, "language": "English", "language_code": lang,
                    "is_generated": generated, "track_name": track_name,
                    "acquisition_method": method, "raw_sha256": raw_digest,
                    "segments": normalize_vtt(payload)}
            archive.write_bytes(gzip.compress(json.dumps(data, ensure_ascii=False).encode("utf-8"), mtime=0))
        except Exception as exc:
            meta.update(status="unavailable", error=type(exc).__name__,
                        error_detail=str(exc)[:200])
            return meta
    segments = data["segments"]
    text = "\n".join(f'[{s["start"]:.2f}] {s["text"]}' for s in segments) + "\n"
    normalized = PRIVATE / f"{position:02d}-{vid}.txt"
    normalized.write_text(text, encoding="utf-8")
    meta.update(status="acquired", language=data["language_code"],
                is_generated=data["is_generated"], track_name=data.get("track_name", ""),
                acquisition_method=method, segment_count=len(segments),
                first_start=segments[0]["start"],
                last_end=max(s["start"] + s["duration"] for s in segments),
                archive_sha256=sha256(archive.read_bytes()).hexdigest(),
                normalized_text_sha256=sha256(normalized.read_bytes()).hexdigest(),
                coverage={"textual": "acquired-not-yet-attested-read", "visual": "not-reviewed",
                          "audio": "not-reviewed"})
    old = OLD_RECORDINGS.get(vid, {})
    if old.get("normalized_text_sha256") == meta["normalized_text_sha256"]:
        meta["coverage"] = old.get("coverage", meta["coverage"])
        for key in ("read_evidence", "reading_evidence"):
            if key in old:
                meta[key] = old[key]
    return meta


def write_manifest(results, publish=False):
    results.sort(key=lambda x: x["position"])
    (PRIVATE / "caption-status.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    if not publish:
        return
    manifest = {"course": "Financial Derivatives and Risk Management", "institution": "IIT Roorkee",
                "instructor": "Prof. J. P. Singh", "course_id": "110107128",
                "official_course_url": "https://nptel.ac.in/courses/110107128",
                "playlist_url": PLAYLIST, "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "expected_entries": 61, "expected_teaching_recordings": 60,
                "sequence_note": "The short introduction is playlist position 1. Put-call parity at position 61 is official lecture 31. Positions 2–31 map to lectures 1–30; positions 32–60 retain lecture numbers 32–60.",
                "coverage_note": "Acquisition is distinct from sequential reading. The chapter authors record reading scope separately. No comprehensive audiovisual audit is claimed.",
                "recordings": results}
    (ROOT / "source-manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    if (PRIVATE / "playlist.json").exists():
        playlist = json.loads((PRIVATE / "playlist.json").read_text(encoding="utf-8-sig"))
    else:
        playlist = {"entries": [
            {"id": r["video_id"], "title": r["title"], "duration": r["duration"]}
            for r in sorted(PUBLISHED["recordings"], key=lambda x: x["position"])
        ]}
    entries = list(enumerate(playlist["entries"], 1))
    results = []
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(acquisition_entry, item) for item in entries]
        for future in as_completed(futures):
            row = future.result()
            results.append(row)
            write_manifest(results)
            print(row["position"], row["status"], row.get("segment_count", 0), row.get("error", ""), flush=True)
    write_manifest(results, publish=True)


if __name__ == "__main__":
    main()
