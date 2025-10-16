#!/usr/bin/env python3
"""Attempt to configure every legacy make config through CMake.

The script mirrors the manual verification process for TRDP's CMake
integration.  It iterates over the ``config`` directory, invokes
``cmake -S . -B <build_dir> -DTRDP_CONFIG=<config>`` for each entry and
collects the exit status as well as the relevant log output.  The
resulting summary helps to identify which presets can be configured in
the current environment and which ones require additional toolchains or
environment variables.

The script does not attempt to build the targets.  It focuses on the
configuration step because that is where missing cross-compilers or
platform SDKs typically surface.  Run it from the repository root:

```
python3 scripts/verify_cmake_configs.py
```

Optional arguments allow selecting a subset of configurations or
changing the base build directory.  See ``--help`` for details.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Set, Tuple

GENERATOR_TOOL_HINTS = {
    "Ninja": "ninja",
    "Unix Makefiles": "make",
}


def list_configs(config_root: Path, selection: Iterable[str] | None) -> List[str]:
    if selection:
        return list(selection)
    return sorted(p.name for p in config_root.iterdir() if p.is_file())


def query_available_generators() -> Set[str]:
    """Return the set of generators that the local CMake installation supports."""

    try:
        completed = subprocess.run(
            ["cmake", "-E", "capabilities"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        # Either CMake is missing entirely or the capabilities command failed.
        # In both cases we simply return an empty set so the caller can decide
        # how to proceed without crashing.
        return set()

    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return set()

    generators = payload.get("generators") or []
    return {entry.get("name", "") for entry in generators if entry.get("name")}


def configure_config(source_dir: Path, build_root: Path, config: str, generator: str | None) -> Tuple[bool, str]:
    build_dir = build_root / config
    build_dir.mkdir(parents=True, exist_ok=True)

    cmd = ["cmake", "-S", str(source_dir), "-B", str(build_dir), f"-DTRDP_CONFIG={config}"]
    if generator:
        cmd.extend(["-G", generator])

    try:
        completed = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        return True, completed.stdout
    except subprocess.CalledProcessError as exc:
        return False, exc.stdout


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description="Verify TRDP CMake configurations")
    parser.add_argument(
        "configs",
        nargs="*",
        help="Specific configuration files to test (defaults to every file in config/)",
    )
    parser.add_argument(
        "--source-dir",
        default=Path.cwd(),
        type=Path,
        help="Path to the TRDP source tree (defaults to current directory)",
    )
    parser.add_argument(
        "--config-root",
        default=None,
        type=Path,
        help="Override the path to the legacy config directory (defaults to <source>/config)",
    )
    parser.add_argument(
        "--build-root",
        default=Path("cmake-config-check"),
        type=Path,
        help="Directory used to store per-config CMake caches",
    )
    parser.add_argument(
        "--generator",
        default=None,
        help="Optional CMake generator to force (e.g. Ninja)",
    )
    parser.add_argument(
        "--clean", action="store_true", help="Delete the build root before running the checks"
    )

    args = parser.parse_args(argv)

    if args.generator:
        generators = query_available_generators()
        if generators and args.generator not in generators:
            parser.error(
                "Requested CMake generator '{gen}' is not available. Install the matching build "
                "tool or omit --generator to let CMake choose a default.\n"
                "Available generators: {available}".format(
                    gen=args.generator, available=", ".join(sorted(generators)) or "unknown"
                )
            )
        tool_hint = GENERATOR_TOOL_HINTS.get(args.generator)
        if tool_hint and shutil.which(tool_hint) is None:
            parser.error(
                "Requested CMake generator '{gen}' requires the '{tool}' executable, which was "
                "not found in PATH. Install it or omit --generator to use the default.".format(
                    gen=args.generator, tool=tool_hint
                )
            )

    source_dir = args.source_dir.resolve()
    config_root = (args.config_root or (source_dir / "config")).resolve()
    build_root = args.build_root.resolve()

    if not config_root.is_dir():
        parser.error(f"Config directory '{config_root}' does not exist")

    if args.clean and build_root.exists():
        shutil.rmtree(build_root)

    configs = list_configs(config_root, args.configs)
    if not configs:
        print("No configuration files found", file=sys.stderr)
        return 1

    print(f"Testing {len(configs)} configurations...")
    successes: List[str] = []
    failures: List[Tuple[str, str]] = []

    for cfg in configs:
        print(f"\n=== {cfg} ===")
        ok, output = configure_config(source_dir, build_root, cfg, args.generator)
        print(output.strip())
        if ok:
            successes.append(cfg)
        else:
            failures.append((cfg, output))

    print("\nSummary")
    print("-------")
    print(f"Succeeded: {len(successes)}")
    for cfg in successes:
        print(f"  - {cfg}")
    print(f"Failed:    {len(failures)}")
    for cfg, _ in failures:
        print(f"  - {cfg}")

    if failures:
        print(
            "\nThe failing configurations typically require vendor-specific toolchains "
            "or environment variables.  Inspect the output above for details."
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
