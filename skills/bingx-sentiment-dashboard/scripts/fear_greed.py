"""Fetch Fear & Greed Index data from alternative.me."""
import argparse
import json
import subprocess
import sys


API_URL = "https://api.alternative.me/fng/"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    if args.limit < 1:
        print(json.dumps({"error": "limit must be greater than 0"}))
        sys.exit(1)

    url = f"{API_URL}?limit={args.limit}"
    try:
        completed = subprocess.run(
            ["curl", "-sS", "-m", "20", url],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
    except subprocess.CalledProcessError as exc:
        print(json.dumps({"error": exc.stderr.strip() or "curl request failed", "url": url}))
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(json.dumps({"error": f"Invalid JSON: {exc}", "url": url}))
        sys.exit(1)

    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
