"""Compare local dev consumption (CPU, memory, power) of different ways to run Postgres/Redis (macOS).

Matrix (you set up each case yourself before running the script, then declare it via flags):

    --runtime none   --workload idle           # nothing started
    --runtime docker --workload idle           # Docker Desktop + `docker compose ... up postgres redis`
    --runtime docker --workload transactions
    --runtime podman --workload idle           # podman machine + compose
    --runtime podman --workload transactions
    --runtime brew   --workload idle           # brew services postgresql/redis
    --runtime brew   --workload transactions

For `transactions`, the DB must be migrated and seeded. Seed once (`flask sandbox -n industrial`), dump it:

    pg_dump -Fc -f consumption_results/industrial.dump "$DATABASE_URL"

then restore it on the first run of each runtime instead of re-seeding (~2s):

    ... --runtime podman --workload idle --restore-dump consumption_results/industrial.dump

Before each case with a DB, the script runs `VACUUM ANALYZE` + `CHECKPOINT`, then waits `--settle` seconds.

Setup variants are saved as separate cases with `--variant <label>`, e.g. native arm64 Postgres:

    docker compose -f docker-compose-backend.yml -f docker-compose-backend.arm64.yml up postgres redis
    ... --runtime docker --workload idle --variant arm64

Usage (from the `api/` directory):

    uv run python src/pcapi/scripts/evaluate_consumption.py --runtime docker --workload transactions --duration 10

Each run (over)writes `<output-dir>/<runtime>_<workload>.csv` (per-interval samples) and replaces its line in
`<output-dir>/summary.csv` (one line per matrix case).

Power sources (both are recorded):
- `sudo powermetrics`: CPU/GPU/ANE (SoC) power every interval. Requires admin rights: the sudo password is asked
  once at startup, then `powermetrics` keeps running as root until the end of the run (even if the rights expire).
  The run aborts if sudo fails; use `--no-powermetrics` to skip it.
- `ioreg` battery telemetry (`SystemLoad`): whole machine incl. display, no root needed, but only refreshes every
  ~60s. Keep brightness constant.
"""

import argparse
import csv
import ctypes
import datetime
import os
import queue
import random
import re
import statistics
import subprocess
import threading
import time
from collections.abc import Sequence
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

import psutil
import psycopg2
import redis
from dotenv import load_dotenv


RUNTIMES = ("none", "docker", "podman", "brew")
WORKLOADS = ("idle", "transactions")
MATRIX = [
    ("none", "idle"),
    ("docker", "idle"),
    ("docker", "transactions"),
    ("podman", "idle"),
    ("podman", "transactions"),
    ("brew", "idle"),
    ("brew", "transactions"),
]

# Processes attributed to each runtime (matched on process name, case-insensitive).
# Shared by docker and podman (counted in both groups, ignored when checking for another runtime running):
# - the VM: Docker Desktop and Podman (applehv) both run it through Apple's Virtualization framework,
# - the compose client: `podman compose` delegates to the `docker-compose` binary.
_VM_PROCESS = "com.apple.virtualization.virtualmachine"
_COMPOSE_PROCESS = "docker-compose"
SHARED_PROCESSES = {_VM_PROCESS, _COMPOSE_PROCESS}
RUNTIME_PROCESS_MATCHERS: dict[str, tuple[str, ...]] = {
    "docker": ("docker", _VM_PROCESS),  # "docker" also matches "docker-compose"
    "podman": ("podman", "gvproxy", "vfkit", "krunkit", _VM_PROCESS, _COMPOSE_PROCESS),
    "brew": ("postgres", "redis-server"),
}

REDIS_KEY_PREFIX = "evaluate_consumption:"


# --------------------------------------------------------------------------------------------------
# Power
# --------------------------------------------------------------------------------------------------

_POWERMETRICS_RE = {
    "cpu_mw": re.compile(r"^CPU Power: (\d+) mW", re.MULTILINE),
    "gpu_mw": re.compile(r"^GPU Power: (\d+) mW", re.MULTILINE),
    "ane_mw": re.compile(r"^ANE Power: (\d+) mW", re.MULTILINE),
    "combined_mw": re.compile(r"^Combined Power \(CPU \+ GPU \+ ANE\): (\d+) mW", re.MULTILINE),
}
_IOREG_SYSTEM_LOAD_RE = re.compile(r'"SystemLoad"=(\d+)')
_IOREG_UPDATE_TIME_RE = re.compile(r'"UpdateTime" = (\d+)')
_IOREG_EXTERNAL_RE = re.compile(r'"ExternalConnected" = (Yes|No)')


class PowerMetricsSampler:
    """Streams `sudo powermetrics` in a background thread, one sample per interval.

    The measurement loop is driven by these samples (`next_sample()`), so that each row covers the exact same
    time window as its power sample.
    """

    def __init__(self, interval_seconds: int) -> None:
        self.interval_seconds = interval_seconds
        self.queue: queue.Queue[dict[str, int]] = queue.Queue()
        self.process: subprocess.Popen | None = None

    @staticmethod
    def authenticate() -> bool:
        """Authenticate sudo upfront (blocking), so the password prompt isn't mixed with log lines."""
        if os.geteuid() == 0:
            return True
        if subprocess.run(["sudo", "-n", "true"], capture_output=True, check=False).returncode == 0:
            return True  # credentials already cached
        print("`powermetrics` requires root.", flush=True)
        return subprocess.run(["sudo", "-v"], check=False).returncode == 0

    def start(self) -> None:
        threading.Thread(target=self._run, daemon=True).start()

    def stop(self) -> None:
        if self.process:
            self.process.terminate()

    def drain(self) -> None:
        while not self.queue.empty():
            self.queue.get_nowait()

    def next_sample(self) -> dict[str, int] | None:
        """Block until the next sample (None if powermetrics stalled or died)."""
        try:
            return self.queue.get(timeout=self.interval_seconds * 2 + 5)
        except queue.Empty:
            return None

    def _run(self) -> None:
        self.process = subprocess.Popen(
            # `-n`: credentials are cached by `authenticate()`, fail instead of prompting again.
            # `-b 1`: line-buffered output, otherwise samples get stuck in the pipe buffer.
            ["sudo", "-n", "powermetrics", "--samplers", "cpu_power,gpu_power,ane_power"]
            + ["-i", str(self.interval_seconds * 1000), "-b", "1"],
            stdout=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        assert self.process.stdout
        buffer = ""
        for line in self.process.stdout:
            buffer += line
            if not line.startswith("Combined Power"):  # last power line of each sample
                continue
            sample = {}
            for key, regex in _POWERMETRICS_RE.items():
                if match := regex.search(buffer):
                    sample[key] = int(match.group(1))
            buffer = ""
            self.queue.put(sample)


@dataclass
class BatteryReading:
    update_time: int
    system_load_mw: int


class BatterySampler:
    """Polls `ioreg` battery telemetry (no root). The battery gauge only refreshes every ~60s."""

    POLL_SECONDS = 5

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.readings: list[BatteryReading] = []  # only readings refreshed after the sampler started
        self._unread: list[BatteryReading] = []
        self.external_power: bool | None = None
        self.stop_event = threading.Event()

    def start(self) -> None:
        threading.Thread(target=self._run, daemon=True).start()

    def stop(self) -> None:
        self.stop_event.set()

    def reset(self) -> None:
        """Drop readings collected before the measurement window."""
        with self.lock:
            self.readings, self._unread = [], []

    def pop_new_readings(self) -> list[BatteryReading]:
        with self.lock:
            readings, self._unread = self._unread, []
            return readings

    def all_readings(self) -> list[BatteryReading]:
        with self.lock:
            return list(self.readings)

    def _read(self) -> BatteryReading | None:
        try:
            output = subprocess.check_output(["ioreg", "-rw0", "-c", "AppleSmartBattery"], text=True)
        except (OSError, subprocess.CalledProcessError):
            return None
        load, update_time, external = (
            _IOREG_SYSTEM_LOAD_RE.search(output),
            _IOREG_UPDATE_TIME_RE.search(output),
            _IOREG_EXTERNAL_RE.search(output),
        )
        if external:
            self.external_power = external.group(1) == "Yes"
        if not (load and update_time):
            return None
        return BatteryReading(update_time=int(update_time.group(1)), system_load_mw=int(load.group(1)))

    def _run(self) -> None:
        last_update_time = None
        while not self.stop_event.is_set():
            reading = self._read()
            if reading:
                if last_update_time is None:
                    last_update_time = reading.update_time  # pre-existing value, measured before the run
                elif reading.update_time != last_update_time:
                    last_update_time = reading.update_time
                    with self.lock:
                        self.readings.append(reading)
                        self._unread.append(reading)
            self.stop_event.wait(self.POLL_SECONDS)


# --------------------------------------------------------------------------------------------------
# Processes
# --------------------------------------------------------------------------------------------------


def _matching_processes(matchers: tuple[str, ...]) -> list[psutil.Process]:
    processes = []
    for process in psutil.process_iter(["name"]):
        name = (process.info["name"] or "").lower()
        if any(matcher in name for matcher in matchers):
            processes.append(process)
    return processes


def check_runtime(runtime: str) -> list[str]:
    """Return warnings when running processes don't match the declared runtime."""
    warnings = []
    for other_runtime, matchers in RUNTIME_PROCESS_MATCHERS.items():
        running = sorted(
            {
                process.info["name"]
                for process in _matching_processes(matchers)
                if process.info["name"].lower() not in SHARED_PROCESSES
            }
        )
        if other_runtime == runtime and not running:
            warnings.append(f"declared runtime '{runtime}' but no matching process found ({', '.join(matchers)})")
        if other_runtime != runtime and running:
            warnings.append(f"'{other_runtime}' processes are running and will skew results: {', '.join(running)}")
    return warnings


class _RUsageInfoV2(ctypes.Structure):
    """`struct rusage_info_v2` from <sys/resource.h>."""

    _fields_ = [("ri_uuid", ctypes.c_uint8 * 16)] + [
        (name, ctypes.c_uint64)
        for name in (
            "ri_user_time",
            "ri_system_time",
            "ri_pkg_idle_wkups",
            "ri_interrupt_wkups",
            "ri_pageins",
            "ri_wired_size",
            "ri_resident_size",
            "ri_phys_footprint",
            "ri_proc_start_abstime",
            "ri_proc_exit_abstime",
            "ri_child_user_time",
            "ri_child_system_time",
            "ri_child_pkg_idle_wkups",
            "ri_child_interrupt_wkups",
            "ri_child_pageins",
            "ri_child_elapsed_abstime",
            "ri_diskio_bytesread",
            "ri_diskio_byteswritten",
        )
    ]


_RUSAGE_INFO_V2 = 2
_libproc = ctypes.CDLL("/usr/lib/libproc.dylib", use_errno=True)


def _rusage(pid: int) -> _RUsageInfoV2 | None:
    """Physical footprint (= Activity Monitor "Memory", incl. compressed memory) and disk I/O, no root needed."""
    info = _RUsageInfoV2()
    if _libproc.proc_pid_rusage(pid, _RUSAGE_INFO_V2, ctypes.byref(info)) != 0:
        return None
    return info


@dataclass
class ProcessGroupSample:
    cpu_percent: float = 0.0  # % of one core, can exceed 100
    rss: int = 0  # resident memory: misleading for VMs (excludes compressed memory, shrinks as macOS reclaims)
    footprint: int = 0  # physical footprint: resident + compressed, what Activity Monitor shows
    disk_read: int = 0  # bytes since previous sample
    disk_written: int = 0  # bytes since previous sample


class ProcessGroupSampler:
    """CPU, memory and disk I/O summed over processes matching the runtime."""

    def __init__(self, matchers: tuple[str, ...]) -> None:
        self.matchers = matchers
        self.processes: dict[int, psutil.Process] = {}
        self.disk_counters: dict[int, tuple[int, int]] = {}  # pid -> (read, written) at previous sample
        self.names: set[str] = set()  # every matched process name during the run, for traceability
        self.refresh()

    def refresh(self) -> None:
        # Always scan (even with no matcher, e.g. `none`) so the script's own overhead is the same in every case.
        for process in _matching_processes(self.matchers or ("\0",)):
            if process.pid not in self.processes:
                try:
                    process.cpu_percent(None)  # prime
                except psutil.Error:
                    continue
                self.processes[process.pid] = process
                self.names.add(process.info["name"])
                if usage := _rusage(process.pid):  # prime: only count I/O done during the run
                    self.disk_counters[process.pid] = (usage.ri_diskio_bytesread, usage.ri_diskio_byteswritten)

    def sample(self) -> ProcessGroupSample:
        result = ProcessGroupSample()
        for pid, process in list(self.processes.items()):
            try:
                result.cpu_percent += process.cpu_percent(None)
                result.rss += process.memory_info().rss
            except psutil.Error:
                del self.processes[pid]
                self.disk_counters.pop(pid, None)
                continue
            if usage := _rusage(pid):
                result.footprint += usage.ri_phys_footprint
                previous_read, previous_written = self.disk_counters.get(
                    pid, (usage.ri_diskio_bytesread, usage.ri_diskio_byteswritten)
                )
                result.disk_read += usage.ri_diskio_bytesread - previous_read
                result.disk_written += usage.ri_diskio_byteswritten - previous_written
                self.disk_counters[pid] = (usage.ri_diskio_bytesread, usage.ri_diskio_byteswritten)
        self.refresh()
        return result


# --------------------------------------------------------------------------------------------------
# Workload
# --------------------------------------------------------------------------------------------------

# (weight, name, sql). Reads mimic typical API endpoints; the write is rolled back to keep the DB stable.
QUERIES: list[tuple[int, str, str]] = [
    (
        30,
        "offer_detail",
        """
        SELECT o.id, o.name, o."subcategoryId", v."publicName", s.id, s.price, s.quantity, s."dnBookedQuantity"
        FROM offer o
        JOIN venue v ON v.id = o."venueId"
        LEFT JOIN stock s ON s."offerId" = o.id AND NOT s."isSoftDeleted"
        WHERE o.id = %(offer_id)s
        """,
    ),
    (
        25,
        "venue_offers",
        """
        SELECT o.id, o.name, count(s.id), min(s.price)
        FROM offer o
        LEFT JOIN stock s ON s."offerId" = o.id AND NOT s."isSoftDeleted"
        WHERE o."venueId" = %(venue_id)s AND o."isActive"
        GROUP BY o.id
        ORDER BY o."dateCreated" DESC
        LIMIT 20
        """,
    ),
    (
        20,
        "user_bookings",
        """
        SELECT b.id, b.status, b.amount, o.name
        FROM booking b
        JOIN stock s ON s.id = b."stockId"
        JOIN offer o ON o.id = s."offerId"
        WHERE b."userId" = %(user_id)s
        ORDER BY b."dateCreated" DESC
        LIMIT 50
        """,
    ),
    (
        15,
        "offer_search",
        """
        SELECT id, name FROM offer
        WHERE name ILIKE %(pattern)s AND "isActive" AND validation = 'APPROVED'
        LIMIT 20
        """,
    ),
    (
        10,
        "stock_update",
        """UPDATE stock SET "dnBookedQuantity" = "dnBookedQuantity" + 1 WHERE id = %(stock_id)s""",
    ),
]


@dataclass
class WorkloadStats:
    transactions: int = 0
    errors: int = 0
    late: int = 0  # transactions started behind schedule (backend can't keep up with the rate)
    latencies_ms: list[float] = field(default_factory=list)
    last_error: str | None = None


class TransactionWorkload:
    """Runs Postgres + Redis transactions at a fixed rate, so that every runtime does the same amount of work."""

    def __init__(self, database_url: str, redis_url: str, rate: float) -> None:
        self.rate = rate
        self.rng = random.Random(42)  # deterministic sequence across runs
        self.pg = psycopg2.connect(database_url)
        self.redis = redis.Redis.from_url(redis_url)
        self.redis.ping()
        self.stats = WorkloadStats()
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self._load_ids()

    def _fetch_ids(self, sql: str) -> list:
        with self.pg.cursor() as cursor:
            cursor.execute(sql)
            return [row[0] for row in cursor.fetchall()]

    def _load_ids(self) -> None:
        self.offer_ids = self._fetch_ids("SELECT id FROM offer ORDER BY id LIMIT 5000")
        self.venue_ids = self._fetch_ids('SELECT DISTINCT "venueId" FROM offer ORDER BY 1 LIMIT 2000')
        self.user_ids = self._fetch_ids('SELECT DISTINCT "userId" FROM booking ORDER BY 1 LIMIT 2000')
        self.stock_ids = self._fetch_ids("SELECT id FROM stock ORDER BY id LIMIT 5000")
        names = self._fetch_ids("SELECT name FROM offer ORDER BY id LIMIT 2000")
        self.patterns = [f"%{name[i : i + 4]}%" for name in names if len(name) >= 4 for i in (0, len(name) // 2)]
        self.pg.rollback()
        empty = [
            name
            for name, ids in (("offer", self.offer_ids), ("venue", self.venue_ids), ("booking", self.user_ids))
            if not ids
        ]
        if empty:
            raise RuntimeError(f"No rows in {', '.join(empty)}: is the DB seeded (`flask sandbox -n industrial`)?")

    def start(self) -> None:
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        self.thread.join(timeout=5)
        self._cleanup()

    def snapshot(self) -> WorkloadStats:
        with self.lock:
            return WorkloadStats(
                self.stats.transactions,
                self.stats.errors,
                self.stats.late,
                list(self.stats.latencies_ms),
                self.stats.last_error,
            )

    def _cleanup(self) -> None:
        try:
            keys = list(self.redis.scan_iter(f"{REDIS_KEY_PREFIX}*"))
            if keys:
                self.redis.delete(*keys)
        finally:
            self.pg.close()
            self.redis.close()

    def _transaction(self) -> None:
        weights = [weight for weight, _, _ in QUERIES]
        _, name, sql = self.rng.choices(QUERIES, weights=weights)[0]
        params = {
            "offer_id": self.rng.choice(self.offer_ids),
            "venue_id": self.rng.choice(self.venue_ids),
            "user_id": self.rng.choice(self.user_ids),
            "stock_id": self.rng.choice(self.stock_ids) if self.stock_ids else 0,
            "pattern": self.rng.choice(self.patterns) if self.patterns else "%a%",
        }
        try:
            with self.pg.cursor() as cursor:
                cursor.execute(sql, params)
                rows = cursor.fetchall() if cursor.description else []
            if name == "stock_update":
                self.pg.rollback()
            else:
                self.pg.commit()
        except psycopg2.Error:
            self.pg.rollback()
            raise

        # Cache-like Redis usage, as the API does (cache + counters + recent items).
        cache_key = f"{REDIS_KEY_PREFIX}cache:{name}:{params['offer_id']}"
        self.redis.get(cache_key)
        pipeline = self.redis.pipeline()
        pipeline.set(cache_key, repr(rows)[:2048], ex=60)
        pipeline.incr(f"{REDIS_KEY_PREFIX}counter:{name}")
        pipeline.lpush(f"{REDIS_KEY_PREFIX}recent", params["offer_id"])
        pipeline.ltrim(f"{REDIS_KEY_PREFIX}recent", 0, 99)
        pipeline.execute()

    def _run(self) -> None:
        period = 1 / self.rate
        next_start = time.monotonic()
        while not self.stop_event.is_set():
            now = time.monotonic()
            if now < next_start:
                self.stop_event.wait(next_start - now)
                continue
            late = now - next_start > period
            started = time.perf_counter()
            error = None
            try:
                self._transaction()
            except (psycopg2.Error, redis.RedisError) as exc:
                error = f"{type(exc).__name__}: {exc}".strip()
            elapsed_ms = (time.perf_counter() - started) * 1000
            with self.lock:
                self.stats.transactions += 1
                self.stats.late += late
                self.stats.latencies_ms.append(elapsed_ms)
                if error:
                    self.stats.errors += 1
                    self.stats.last_error = error
            next_start += period


# --------------------------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------------------------


def _mean(values: Sequence[float]) -> float | None:
    return round(statistics.fmean(values), 2) if values else None


def _mean_key(samples: list[dict[str, int]], key: str) -> float | None:
    return _mean([sample[key] for sample in samples if key in sample])


def _percentile(values: list[float], percent: int) -> float | None:
    if len(values) < 2:
        return round(values[0], 2) if values else None
    return round(statistics.quantiles(values, n=100)[percent - 1], 2)


def _load_env() -> None:
    """Same env files as `pcapi.settings` in development (run from `api/`)."""
    original_tz = os.environ.get("TZ")
    load_dotenv(".env.development")
    load_dotenv(".env.local.secret", override=True)
    # `.env.development` sets `TZ=UTC`: keep local time for the logged timestamps.
    if original_tz is None:
        os.environ.pop("TZ", None)
    else:
        os.environ["TZ"] = original_tz
    time.tzset()


def _variant(value: str) -> str:
    if not re.fullmatch(r"[a-z0-9-]+", value):
        raise argparse.ArgumentTypeError("only lowercase letters, digits and dashes")
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--runtime", choices=RUNTIMES, required=True, help="How Postgres/Redis are currently run.")
    parser.add_argument("--workload", choices=WORKLOADS, required=True)
    parser.add_argument("--duration", type=int, default=300, help="Measurement duration in seconds (default: 300).")
    parser.add_argument("--interval", type=int, default=5, help="Sampling interval in seconds (default: 5).")
    parser.add_argument("--rate", type=float, default=20, help="Transactions per second (default: 20).")
    parser.add_argument("--database-url", help="Default: DATABASE_URL from .env.local.secret.")
    parser.add_argument("--redis-url", help="Default: REDIS_URL from env, or redis://localhost:6379.")
    parser.add_argument("--output-dir", type=Path, default=Path("consumption_results"))
    parser.add_argument(
        "--variant",
        type=_variant,
        help="Optional label for a setup variant, saved as a separate case (e.g. `arm64` -> `docker_idle_arm64`).",
    )
    parser.add_argument(
        "--restore-dump",
        type=Path,
        help="Restore this `pg_dump -Fc` dump first (seeded DB, avoids re-seeding for each runtime).",
    )
    parser.add_argument(
        "--no-db-prep",
        action="store_true",
        help="Skip `VACUUM ANALYZE` + `CHECKPOINT` (run by default before each case with a DB).",
    )
    parser.add_argument(
        "--settle",
        type=int,
        default=60,
        help="Seconds to wait before measuring, after DB prep / workload start (default: 60).",
    )
    parser.add_argument(
        "--no-powermetrics",
        action="store_true",
        help="Don't use `sudo powermetrics` (power then only comes from the battery gauge, ~60s resolution).",
    )
    args = parser.parse_args()
    if args.runtime == "none" and args.workload == "transactions":
        parser.error("`--workload transactions` requires a runtime (docker, podman or brew).")
    if args.runtime == "none" and args.restore_dump:
        parser.error("`--restore-dump` requires a runtime (docker, podman or brew).")
    return args


_TOC_EXTENSION_RE = re.compile(r"^\d+; \d+ \d+ EXTENSION - (\S+)", re.MULTILINE)
_EXTENSION_SCHEMA_RE = re.compile(r"CREATE EXTENSION .* WITH SCHEMA (\S+);")


def _restore_list_without_unavailable_extensions(database_url: str, dump_path: Path) -> Path | None:
    """Build a `pg_restore --use-list` file skipping extensions the target server doesn't provide.

    E.g. the `postgis/postgis` image installs `postgis_tiger_geocoder` (unused by pcapi), which brew's postgis lacks.
    Skipped: the extension, its comment and the data of its config tables (in the extension schema).
    Returns None when nothing has to be skipped.
    """
    toc = subprocess.check_output(["pg_restore", "--list", str(dump_path)], text=True)
    connection = psycopg2.connect(database_url)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM pg_available_extensions")
            available = {row[0] for row in cursor.fetchall()}
    finally:
        connection.close()
    unavailable = [name for name in _TOC_EXTENSION_RE.findall(toc) if name not in available]
    if not unavailable:
        return None

    skipped_patterns = []
    for extension in unavailable:
        skipped_patterns += [f" EXTENSION - {extension} ", f" COMMENT - EXTENSION {extension} "]
        # Find the extension schema from its CREATE EXTENSION statement.
        entry = next(line for line in toc.splitlines() if f" EXTENSION - {extension} " in f"{line} ")
        single_entry_list = dump_path.parent / f".{dump_path.name}.entry.list"
        single_entry_list.write_text(entry + "\n")
        sql = subprocess.check_output(
            ["pg_restore", "--use-list", str(single_entry_list), "--file", "-", str(dump_path)], text=True
        )
        single_entry_list.unlink()
        if schema_match := _EXTENSION_SCHEMA_RE.search(sql):
            skipped_patterns += [f" TABLE DATA {schema_match.group(1)} ", f" SEQUENCE SET {schema_match.group(1)} "]

    kept: list[str] = []
    skipped: list[str] = []
    for line in toc.splitlines():
        (skipped if any(pattern in f"{line} " for pattern in skipped_patterns) else kept).append(line)
    print(f"Skipping {len(skipped)} dump entries of unavailable extension(s) {', '.join(unavailable)}:", flush=True)
    for line in skipped:
        print(f"  {line}", flush=True)
    restore_list = dump_path.parent / f".{dump_path.name}.restore.list"
    restore_list.write_text("\n".join(kept) + "\n")
    return restore_list


def restore_dump(database_url: str, dump_path: Path) -> None:
    """Restore a `pg_dump -Fc` dump (e.g. a seeded DB), replacing existing objects. The database must exist."""
    print(f"Restoring {dump_path}...", flush=True)
    started = time.monotonic()
    restore_list = _restore_list_without_unavailable_extensions(database_url, dump_path)
    result = subprocess.run(
        ["pg_restore", "--clean", "--if-exists", "--no-owner", "--no-privileges", "--jobs", "4"]
        + (["--use-list", str(restore_list)] if restore_list else [])
        + ["--dbname", database_url, str(dump_path)],
        check=False,
    )
    if restore_list:
        restore_list.unlink()
    if result.returncode != 0:
        raise SystemExit(f"ERROR: pg_restore failed (exit code {result.returncode}).")
    print(f"Restored in {time.monotonic() - started:.1f}s.", flush=True)


def prepare_database(database_url: str) -> None:
    """Same DB state for every case: fresh statistics, no dead tuples left to vacuum, no dirty pages to flush."""
    print("Preparing database (VACUUM ANALYZE, CHECKPOINT)...", flush=True)
    started = time.monotonic()
    try:
        connection = psycopg2.connect(database_url)
    except psycopg2.Error as exc:
        raise SystemExit(f"ERROR: cannot connect to {database_url}: {exc}".strip()) from exc
    try:
        connection.autocommit = True  # VACUUM can't run inside a transaction
        with connection.cursor() as cursor:
            cursor.execute("VACUUM ANALYZE")
            cursor.execute("CHECKPOINT")
    finally:
        connection.close()
    print(f"Database prepared in {time.monotonic() - started:.1f}s.", flush=True)


def write_summary(path: Path, summary: dict) -> None:
    """Keep one line per matrix case: a new run of a case replaces its previous line."""
    rows: list[dict] = []
    if path.exists():
        with path.open(newline="") as file:
            rows = [row for row in csv.DictReader(file) if row.get("case") != summary["case"]]
    rows.append(summary)
    order = {f"{runtime}_{workload}": index for index, (runtime, workload) in enumerate(MATRIX)}
    # Case = `<runtime>_<workload>[_<variant>]`: variants are listed right after their base case.
    rows.sort(key=lambda row: (order.get("_".join(row["case"].split("_")[:2]), len(order)), row["case"]))
    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(summary), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    _load_env()
    database_url = args.database_url or os.environ.get("DATABASE_URL", "")
    redis_url = args.redis_url or os.environ.get("REDIS_URL", "redis://localhost:6379")
    case = f"{args.runtime}_{args.workload}" + (f"_{args.variant}" if args.variant else "")
    sample_count = max(1, round(args.duration / args.interval))

    warnings = check_runtime(args.runtime)
    for warning in warnings:
        print(f"WARNING: {warning}", flush=True)

    # Authenticate first, so the sudo prompt doesn't get mixed with log lines. `powermetrics` is started right away
    # (it then keeps running as root), so that sudo can't expire during the DB preparation / settle time.
    powermetrics = None
    if not args.no_powermetrics:
        if not PowerMetricsSampler.authenticate():
            raise SystemExit(
                "ERROR: sudo authentication failed (admin rights expired?). Use --no-powermetrics to skip."
            )
        powermetrics = PowerMetricsSampler(args.interval)
        powermetrics.start()
        print("Checking `powermetrics`...", flush=True)
        if powermetrics.next_sample() is None:
            powermetrics.stop()
            raise SystemExit("ERROR: no `powermetrics` sample received. Use --no-powermetrics to skip.")

    battery = BatterySampler()
    battery.start()
    if args.duration < 120:
        print(
            f"NOTE: the battery gauge refreshes every ~60s, a {args.duration}s run gets at most "
            f"{args.duration // 60 + 1} battery reading(s).",
            flush=True,
        )

    if args.restore_dump:
        restore_dump(database_url, args.restore_dump)
    if args.runtime != "none" and not args.no_db_prep:
        prepare_database(database_url)

    workload = None
    if args.workload == "transactions":
        print(f"Connecting to {database_url} and {redis_url}...", flush=True)
        try:
            workload = TransactionWorkload(database_url, redis_url, args.rate)
        except (psycopg2.Error, redis.RedisError, RuntimeError) as exc:
            raise SystemExit(f"ERROR: cannot start the transactions workload: {exc}".strip()) from exc
        workload.start()

    if args.settle:
        # Lets background activity calm down (and warms up the workload) before measuring.
        print(f"Settling for {args.settle}s before measuring...", flush=True)
        time.sleep(args.settle)

    if powermetrics:
        # Discard samples collected so far: the arrival of the next one marks the measurement window start.
        powermetrics.drain()
        if powermetrics.next_sample() is None:
            raise SystemExit("ERROR: `powermetrics` stopped sending samples.")

    # Measurement window starts now.
    battery.reset()
    runtime_processes = ProcessGroupSampler(RUNTIME_PROCESS_MATCHERS.get(args.runtime, ()))
    own_process = psutil.Process()
    own_process.cpu_percent(None)
    psutil.cpu_times_percent(None)  # prime: next calls are computed over the elapsed interval
    transactions_before = workload.snapshot().transactions if workload else 0
    previous_transactions = transactions_before
    started_at = datetime.datetime.now()
    rows: list[dict] = []

    print(f"[{case}] measuring for {args.duration}s every {args.interval}s (Ctrl+C to stop early)...", flush=True)
    try:
        for _ in range(sample_count):
            if powermetrics:
                power = powermetrics.next_sample()
                if power is None:
                    print("WARNING: `powermetrics` stalled, no power for this interval.", flush=True)
                    power = {}
            else:
                time.sleep(args.interval)
                power = {}
            cpu = psutil.cpu_times_percent(None)
            memory = psutil.virtual_memory()
            runtime = runtime_processes.sample()
            new_battery = battery.pop_new_readings()
            stats = workload.snapshot() if workload else WorkloadStats()
            row = {
                "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
                "cpu_percent": round(100 - cpu.idle, 2),
                "cpu_user_percent": cpu.user,
                "cpu_system_percent": cpu.system,
                "memory_used_gib": round(memory.used / 1024**3, 3),
                "memory_percent": memory.percent,
                "runtime_cpu_percent": round(runtime.cpu_percent, 2),
                "runtime_footprint_mib": round(runtime.footprint / 1024**2, 1),
                "runtime_rss_mib": round(runtime.rss / 1024**2, 1),
                "runtime_disk_read_mib": round(runtime.disk_read / 1024**2, 3),
                "runtime_disk_written_mib": round(runtime.disk_written / 1024**2, 3),
                "script_cpu_percent": own_process.cpu_percent(None),
                "battery_system_load_mw": new_battery[-1].system_load_mw if new_battery else None,
                "powermetrics_combined_mw": power.get("combined_mw"),
                "powermetrics_cpu_mw": power.get("cpu_mw"),
                "powermetrics_gpu_mw": power.get("gpu_mw"),
                "powermetrics_ane_mw": power.get("ane_mw"),
                "transactions": stats.transactions - previous_transactions,
                "transaction_errors_total": stats.errors,
            }
            previous_transactions = stats.transactions
            rows.append(row)
            print(
                f"[{row['timestamp']}] CPU {row['cpu_percent']}% | "
                f"Mem {row['memory_used_gib']} GiB ({row['memory_percent']}%) | "
                f"{args.runtime}: CPU {row['runtime_cpu_percent']}% Mem {row['runtime_footprint_mib']} MiB "
                f"Disk W {row['runtime_disk_written_mib']} MiB | "
                f"Battery load {row['battery_system_load_mw'] or '-'} mW | "
                f"powermetrics {row['powermetrics_combined_mw'] or '-'} mW | "
                f"tx {row['transactions']} (errors {stats.errors})",
                flush=True,
            )
            if stats.last_error and stats.errors == 1:
                print(f"  first transaction error: {stats.last_error}", flush=True)
    except KeyboardInterrupt:
        print("Interrupted, writing partial results.", flush=True)
    finally:
        actual_duration = (datetime.datetime.now() - started_at).total_seconds()
        stats = workload.snapshot() if workload else WorkloadStats()
        if workload:
            workload.stop()
        if powermetrics:
            powermetrics.stop()
        battery.stop()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    samples_path = args.output_dir / f"{case}.csv"
    if rows:
        with samples_path.open("w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    def column(name: str) -> list[float]:
        return [row[name] for row in rows if row[name] is not None]

    def energy_wh(avg_mw: float | None) -> float | None:
        return round(avg_mw / 1000 * actual_duration / 3600, 4) if avg_mw is not None else None

    battery_loads = [reading.system_load_mw for reading in battery.all_readings()]
    avg_battery_load = _mean(battery_loads)
    avg_combined_power = _mean(column("powermetrics_combined_mw"))
    transactions = stats.transactions - transactions_before
    summary = {
        "case": case,
        "started_at": started_at.isoformat(timespec="seconds"),
        "duration_s": round(actual_duration, 1),
        "samples": len(rows),
        "avg_cpu_percent": _mean(column("cpu_percent")),
        "avg_memory_used_gib": _mean(column("memory_used_gib")),
        "avg_runtime_cpu_percent": _mean(column("runtime_cpu_percent")),
        "avg_runtime_footprint_mib": _mean(column("runtime_footprint_mib")),
        "avg_runtime_rss_mib": _mean(column("runtime_rss_mib")),
        "runtime_disk_read_mib": round(sum(column("runtime_disk_read_mib")), 1),
        "runtime_disk_written_mib": round(sum(column("runtime_disk_written_mib")), 1),
        "avg_script_cpu_percent": _mean(column("script_cpu_percent")),
        "powermetrics_samples": len(column("powermetrics_combined_mw")),
        "avg_powermetrics_combined_mw": avg_combined_power,
        "avg_powermetrics_cpu_mw": _mean(column("powermetrics_cpu_mw")),
        "avg_powermetrics_gpu_mw": _mean(column("powermetrics_gpu_mw")),
        "avg_powermetrics_ane_mw": _mean(column("powermetrics_ane_mw")),
        "powermetrics_energy_wh": energy_wh(avg_combined_power),
        "battery_readings": len(battery_loads),
        "avg_battery_system_load_mw": avg_battery_load,
        "battery_energy_wh": energy_wh(avg_battery_load),
        "external_power": battery.external_power,
        "target_tx_per_s": args.rate if workload else None,
        "transactions": transactions if workload else None,
        "achieved_tx_per_s": round(transactions / actual_duration, 2) if workload else None,
        "transaction_errors": stats.errors if workload else None,
        "late_transactions": stats.late if workload else None,
        "p50_latency_ms": _percentile(stats.latencies_ms, 50),
        "p95_latency_ms": _percentile(stats.latencies_ms, 95),
        "runtime_processes": ", ".join(sorted(runtime_processes.names)),
        "warnings": " | ".join(warnings),
    }
    summary_path = args.output_dir / "summary.csv"
    write_summary(summary_path, summary)

    print("\nSummary:", flush=True)
    for key, value in summary.items():
        print(f"  {key}: {value}", flush=True)
    print(f"\nSamples: {samples_path}\nSummary ({case} line replaced): {summary_path}", flush=True)


if __name__ == "__main__":
    main()
