"""Compare a served static edition with an explicitly named Git commit."""
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
import argparse
import gzip
import json
import subprocess
import tarfile
import time

ROOT = Path(__file__).resolve().parents[1]


def committed_files(commit):
    """Read committed bytes, independent of modified working-tree files."""
    revision = subprocess.check_output(
        ["git", "rev-parse", "--verify", commit + "^{commit}"], cwd=ROOT,
        text=True).strip()
    archive = subprocess.check_output(["git", "archive", revision], cwd=ROOT)
    with tarfile.open(fileobj=BytesIO(archive)) as stream:
        files = {member.name: stream.extractfile(member).read()
                 for member in stream.getmembers()
                 if member.isfile() and not any(
                     part.startswith(".") for part in Path(member.name).parts)}
    required = {"index.html", "source-manifest.json", "artifact-manifest.json"}
    required.update(f"ch{i:02d}.html" for i in range(1, 25))
    if not required <= files.keys():
        raise ValueError("Named commit does not contain the complete edition")
    return revision, files


def fetch(url):
    request = Request(url, headers={"Accept-Encoding": "identity",
                                    "User-Agent": "LectureEditionVerifier/1"})
    for attempt in range(3):
        try:
            with urlopen(request, timeout=35) as response:
                data = response.read()
                if response.headers.get("Content-Encoding") == "gzip":
                    data = gzip.decompress(data)
                return response.status, data, None
        except HTTPError as exc:
            if exc.code >= 500 or exc.code == 429:
                if attempt < 2:
                    time.sleep(attempt + 1)
                    continue
            return exc.code, b"", str(exc)
        except (URLError, TimeoutError, OSError) as exc:
            if attempt < 2:
                time.sleep(attempt + 1)
                continue
            return None, b"", str(exc)


def main(commit, base_url, destination, workers):
    if not base_url.startswith("https://"):
        raise ValueError("Live verification requires an HTTPS base URL")
    revision, files = committed_files(commit)
    base_url = base_url.rstrip("/") + "/"

    def compare(item):
        name, expected = item
        url = base_url + quote(name, safe="/") + "?release=" + revision
        status, actual, error = fetch(url)
        expected_hash = sha256(expected).hexdigest()
        actual_hash = sha256(actual).hexdigest() if status == 200 else None
        return {"path": name, "http_status": status,
                "expected_bytes": len(expected),
                "received_bytes": len(actual),
                "expected_sha256": expected_hash,
                "served_sha256": actual_hash,
                "matches": status == 200 and actual_hash == expected_hash,
                "error": error}

    with ThreadPoolExecutor(max_workers=workers) as pool:
        records = list(pool.map(compare, sorted(files.items())))
    private = []
    for name in ["README.txt", "HANDOFF.md", ".git/config",
                 "work/workflow-report/index.html", "work/acquisition/"]:
        status, _, error = fetch(base_url + name + "?release=" + revision)
        private.append({"path": name, "http_status": status,
                        "not_served": status in (403, 404, 410),
                        "error": error if status is None else None})
    failures = [r["path"] for r in records if not r["matches"]]
    failures += [r["path"] for r in private if not r["not_served"]]
    report = {
        "status": "pass" if not failures else "fail",
        "release_commit": revision, "base_url": base_url,
        "verified_file_count": len(records), "files": records,
        "private_path_checks": private, "failures": failures,
        "scope": "HTTP delivery and exact served bytes of every non-hidden file in the named Git archive; all24chapterpages explicitly required. Hidden repository configuration is excluded from the served-file claim. This establishes publication correspondence, not scientific correctness.",
        "self_verification": "The report verifies the named earlier commit. A newly written report is not included in that earlier archive; a later documentation commit must be distinguished from this payload commit.",
    }
    output = Path(destination)
    if not output.is_absolute():
        output = ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n",
                      encoding="utf-8", newline="\n")
    print(json.dumps({"status": report["status"], "commit": revision,
                      "files": len(records), "failures": failures}, indent=2))
    return bool(failures)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", required=True)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--report", default="validation/live-publication-checks.json")
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    if not 1 <= args.workers <= 12:
        parser.error("workers must lie between1and12")
    raise SystemExit(main(args.commit, args.base_url, args.report, args.workers))
