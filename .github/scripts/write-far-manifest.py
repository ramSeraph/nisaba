#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct
from urllib.parse import quote

STTABLE_MAGIC = 0x7EB2F35C
STTABLE_VERSION = 1
ENTRY_COUNT_BYTES = 8
KEY_LENGTH_BYTES = 4


def far_entries(path: Path) -> list[dict[str, int | str]]:
    data = path.read_bytes()
    if len(data) < 16:
        raise ValueError(f"{path} is too small to be a FAR archive")

    magic, version = struct.unpack_from("<II", data, 0)
    if magic != STTABLE_MAGIC:
        raise ValueError(f"{path} does not look like an STTable FAR archive")
    if version != STTABLE_VERSION:
        raise ValueError(f"Unsupported FAR version {version} in {path}")

    entry_count = struct.unpack_from("<q", data, len(data) - ENTRY_COUNT_BYTES)[0]
    trailer_start = len(data) - ENTRY_COUNT_BYTES * (entry_count + 2)
    if trailer_start < 8:
        raise ValueError(f"Corrupt FAR trailer in {path}")

    leading_count = struct.unpack_from("<q", data, trailer_start)[0]
    if leading_count != entry_count:
        raise ValueError(f"Corrupt FAR index count in {path}")

    positions = list(
        struct.unpack_from(f"<{entry_count}q", data, trailer_start + ENTRY_COUNT_BYTES)
    )
    entries: list[dict[str, int | str]] = []
    for index_offset, position in enumerate(positions):
        if position < 8 or position >= trailer_start:
            raise ValueError(f"Corrupt FAR entry offset {position} in {path}")
        next_position = (
            positions[index_offset + 1]
            if index_offset + 1 < len(positions)
            else trailer_start
        )
        key_length = struct.unpack_from("<i", data, position)[0]
        if key_length < 0:
            raise ValueError(f"Negative FAR key length in {path}")
        key_start = position + KEY_LENGTH_BYTES
        key_end = key_start + key_length
        if key_end > next_position:
            raise ValueError(f"Corrupt FAR key bounds in {path}")
        entries.append(
            {
                "key": data[key_start:key_end].decode("utf-8"),
                "fst_start": key_end,
                "fst_end": next_position,
            }
        )
    return sorted(entries, key=lambda entry: str(entry["key"]))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Write a JSON manifest of FAR files and their internal keys."
    )
    parser.add_argument("--scripts-root", required=True, type=Path)
    parser.add_argument("--release-dir", required=True)
    parser.add_argument("--release-name", required=True)
    parser.add_argument("--repo-url", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("far_files", nargs="+", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scripts_root = args.scripts_root.resolve()
    repo_url = args.repo_url.rstrip("/")

    files = []
    for far_path in sorted(args.far_files):
        resolved = far_path.resolve()
        entries = far_entries(resolved)
        files.append(
            {
                "path": str(resolved.relative_to(scripts_root)),
                "url": (
                    f"{repo_url}/releases/download/{quote(args.release_name)}/"
                    f"{quote(resolved.name)}"
                ),
                "keys": [str(entry["key"]) for entry in entries],
                "entries": entries,
            }
        )

    manifest = {
        "release_name": args.release_name,
        "release_dir": args.release_dir,
        "files": files,
    }
    args.output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
