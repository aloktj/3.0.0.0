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
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Tuple


def list_configs(config_root: Path, selection: Iterable[str] | None) -> List[str]:
    if selection:
        return list(selection)
    return sorted(p.name for p in config_root.iterdir() if p.is_file())


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
