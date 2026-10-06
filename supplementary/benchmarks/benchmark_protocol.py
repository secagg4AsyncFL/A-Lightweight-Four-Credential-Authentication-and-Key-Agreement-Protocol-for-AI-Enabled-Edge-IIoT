#!/usr/bin/env python3
"""Reproducible host benchmark for the protocol's measured primitives.

The protocol uses the leftmost 160 bits of SHA-256 for serialized hash fields.
The benchmark times the underlying full SHA-256 operation; field truncation is
not included in the primitive timing because it is a serialization step. The manuscript does not mandate a
particular fuzzy-extractor construction, so the script includes a small
deterministic Gen/Rep reference implementation: SHA-256 binds the biometric
sample to helper data and HMAC-SHA-256 derives the reproduced key. This is a
reference implementation for timing, not a claim that it is the final
deployment fuzzy extractor. All timings exclude network I/O, display work,
random generation, and serialization.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import platform
import statistics
import sys
import time
from pathlib import Path


HASH_PAYLOAD = bytes(range(64))
BIOMETRIC = bytes((i * 37 + 11) % 256 for i in range(256))
FE_SALT = bytes(range(16))
FE_HELPER = FE_SALT + hashlib.sha256(BIOMETRIC).digest()
PROTOCOL_HASH_BYTES = 20


def cpu_model() -> str:
    """Return a best-effort physical CPU label without requiring admin rights."""
    if sys.platform == "win32":
        try:
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"HARDWARE\DESCRIPTION\System\CentralProcessor\0",
            )
            value, _ = winreg.QueryValueEx(key, "ProcessorNameString")
            return str(value).strip()
        except Exception:
            pass
    try:
        text = Path("/proc/cpuinfo").read_text(encoding="utf-8", errors="ignore")
        for line in text.splitlines():
            if line.lower().startswith(("model name", "hardware")):
                return line.split(":", 1)[-1].strip()
    except Exception:
        pass
    return platform.processor() or "unavailable"


def hash_once() -> bytes:
    return hashlib.sha256(HASH_PAYLOAD).digest()


def protocol_hash_160(payload: bytes) -> bytes:
    """Return the 160-bit protocol-field representation of a SHA-256 digest."""
    return hashlib.sha256(payload).digest()[:PROTOCOL_HASH_BYTES]


def fuzzy_rep_reference() -> bytes:
    """Reference Gen/Rep reproduction for a matching 256-byte sample."""
    salt = FE_HELPER[:16]
    expected_digest = FE_HELPER[16:]
    if hashlib.sha256(BIOMETRIC).digest() != expected_digest:
        raise ValueError("biometric helper mismatch")
    first = hmac.new(salt, BIOMETRIC, hashlib.sha256).digest()
    return hmac.new(first, b"CMC-FE-REP", hashlib.sha256).digest()


def user_session() -> None:
    for _ in range(15):
        hash_once()
    fuzzy_rep_reference()


def edge_session() -> None:
    for _ in range(21):
        hash_once()


def sensor_session() -> None:
    for _ in range(6):
        hash_once()


def benchmark(fn, iterations: int, batch_size: int) -> dict[str, float]:
    for _ in range(min(10_000, iterations)):
        fn()
    samples: list[float] = []
    batches = max(1, iterations // batch_size)
    for _ in range(batches):
        start = time.perf_counter_ns()
        for _ in range(batch_size):
            fn()
        elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000
        samples.append(elapsed_ms / batch_size)
    samples.sort()
    p95_index = min(len(samples) - 1, int(0.95 * len(samples)))
    return {
        "mean_ms": statistics.fmean(samples),
        "median_ms": statistics.median(samples),
        "p95_ms": samples[p95_index],
        "stdev_ms": statistics.stdev(samples) if len(samples) > 1 else 0.0,
        "samples": len(samples),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=200_000)
    parser.add_argument("--batch-size", type=int, default=1_000)
    parser.add_argument("--output", type=Path, default=Path("benchmark_results.json"))
    args = parser.parse_args()
    if args.iterations < args.batch_size or args.batch_size <= 0:
        raise SystemExit("iterations must be >= batch-size > 0")

    results = {
        "metadata": {
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "cpu_model": cpu_model(),
            "logical_cpus": os.cpu_count(),
            "python": sys.version.split()[0],
            "hash": "SHA-256 via hashlib/OpenSSL backend",
            "iterations": args.iterations,
            "batch_size": args.batch_size,
        },
        "primitive": {
            "sha256_64B": benchmark(hash_once, args.iterations, args.batch_size),
            "fuzzy_rep_reference_256B": benchmark(
                fuzzy_rep_reference, args.iterations // 4, args.batch_size
            ),
        },
        "protocol_roles": {
            "LD_user_15H_plus_FE": benchmark(
                user_session, args.iterations // 4, max(10, args.batch_size // 4)
            ),
            "EN_21H": benchmark(
                edge_session, args.iterations // 4, max(10, args.batch_size // 4)
            ),
            "SN_6H": benchmark(
                sensor_session, args.iterations // 4, max(10, args.batch_size // 4)
            ),
        },
    }
    results["protocol_roles"]["sum_median_ms"] = sum(
        results["protocol_roles"][role]["median_ms"]
        for role in ("LD_user_15H_plus_FE", "EN_21H", "SN_6H")
    )
    args.output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
