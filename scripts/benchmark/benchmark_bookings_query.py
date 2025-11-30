"""
Booking Queries Performance Benchmark Script

Measures performance metrics for the `get_bookings_pro` query patterns.
Compares PostgreSQL (baseline) vs TimescaleDB implementations.

Usage:
    python ./scripts/benchmark/benchmark_bookings_query.py --service postgres    --output ./results/baseline.json
    python ./scripts/benchmark/benchmark_bookings_query.py --service timescaledb --output ./results/timescaledb_with_hypertable.json
    python ./scripts/benchmark/benchmark_bookings_query.py --service timescaledb --output ./results/timescaledb_with_compression.json
    python ./scripts/benchmark/benchmark_bookings_query.py --service timescaledb --output ./results/timescaledb_with_continuous_aggregates.json

Metrics collected:
    - Query execution time (ms)
    - Memory usage (MB)
    - Disk I/O (reads/writes)
    - CPU usage (%)
    - Result set size
"""

import argparse
import json
import logging
import resource
import sys
import time
from datetime import datetime, timedelta
from typing import Any, Optional

import psycopg2
import psycopg2.extras

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

POSTGRES_PORT = 5434
TIMESCALEDB_PORT = 5435


class PerformanceMetrics:
    def __init__(self, query_name: str):
        self.query_name = query_name
        self.execution_time_ms = 0.0
        self.memory_usage_mb = 0.0
        self.result_count = 0
        self.error: Optional[str] = None
        self.query_plan = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "query_name": self.query_name,
            "execution_time_ms": round(self.execution_time_ms, 2),
            "memory_usage_mb": round(self.memory_usage_mb, 2),
            "result_count": self.result_count,
            "error": self.error,
        }


class BookingQueryBenchmark:
    """Benchmark suite for booking queries."""

    def __init__(self, service: str):
        host = "0.0.0.0"
        port = POSTGRES_PORT if service == "postgres" else TIMESCALEDB_PORT
        user = "pass_culture"
        password = "passq"
        dbname = "pass_culture"

        self.conn_str = (
            f"host={host} port={port} dbname={dbname} user={user} password={password}"
        )
        self.conn = None
        self.test_user_id = None
        self.test_offerer_id = None
        self.test_venue_id = None
        self.results = []

    def connect(self):
        logger.info("Connecting to database...")
        self.conn = psycopg2.connect(self.conn_str)
        self.conn.autocommit = True

    def disconnect(self):
        if self.conn:
            self.conn.close()

    def get_memory_usage_mb(self) -> float:
        usage = resource.getrusage(resource.RUSAGE_SELF)
        return usage.ru_maxrss / 1024

    def get_disk_sizes(self) -> dict[str, Any]:
        stats = {
            "table_size_bytes": 0,
            "table_size_pretty": "0 bytes",
            "indexes_size_bytes": 0,
            "indexes_size_pretty": "0 bytes",
            "total_size_bytes": 0,
            "total_size_pretty": "0 bytes",
            "compression_stats": None,
        }

        try:
            if not self.conn:
                raise ValueError("Database connection is not established")
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        pg_table_size('booking') as table_size,
                        pg_indexes_size('booking') as indexes_size,
                        pg_total_relation_size('booking') as total_size,
                        pg_size_pretty(pg_table_size('booking')) as table_size_pretty,
                        pg_size_pretty(pg_indexes_size('booking')) as indexes_size_pretty,
                        pg_size_pretty(pg_total_relation_size('booking')) as total_size_pretty;
                """)
                result = cursor.fetchone()
                if result:
                    stats["table_size_bytes"] = result[0]
                    stats["indexes_size_bytes"] = result[1]
                    stats["total_size_bytes"] = result[2]
                    stats["table_size_pretty"] = result[3]
                    stats["indexes_size_pretty"] = result[4]
                    stats["total_size_pretty"] = result[5]

                cursor.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM pg_extension WHERE extname = 'timescaledb'
                    );
                """)
                timescale_result = cursor.fetchone()
                is_timescaledb = timescale_result[0] if timescale_result else False

                if is_timescaledb:
                    cursor.execute("""
                        SELECT
                            COUNT(*) as total_chunks,
                            COUNT(*) FILTER (WHERE is_compressed) as compressed_chunks,
                            SUM(uncompressed_heap_size) as total_uncompressed,
                            SUM(compressed_heap_size) as total_compressed,
                            CASE
                                WHEN SUM(compressed_heap_size) > 0 THEN
                                    ROUND((SUM(uncompressed_heap_size)::numeric / SUM(compressed_heap_size)::numeric), 2)
                                ELSE NULL
                            END as compression_ratio
                        FROM timescaledb_information.chunks
                        WHERE hypertable_name = 'booking';
                    """)
                    comp_result = cursor.fetchone()
                    if comp_result and comp_result[0]:
                        stats["compression_stats"] = {
                            "total_chunks": comp_result[0],
                            "compressed_chunks": comp_result[1],
                            "uncompressed_bytes": comp_result[2] or 0,
                            "compressed_bytes": comp_result[3] or 0,
                            "compression_ratio": float(comp_result[4])
                            if comp_result[4]
                            else None,
                        }

        except Exception as e:
            logger.warning(f"Failed to get disk sizes: {e}")

        return stats

    def find_test_entities(self):
        """Find test entities (user, offerer, venue) with bookings for realistic queries."""
        logger.info("Finding test entities with bookings...")

        if not self.conn:
            raise ValueError("Database connection is not established")
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    uo."userId",
                    uo."offererId",
                    COUNT(DISTINCT b.id) as booking_count
                FROM user_offerer uo
                JOIN booking b ON b."offererId" = uo."offererId"
                WHERE uo."validationStatus" = 'VALIDATED'
                GROUP BY uo."userId", uo."offererId"
                HAVING COUNT(DISTINCT b.id) > 10
                ORDER BY COUNT(DISTINCT b.id) DESC
                LIMIT 1
                """
            )
            result = cursor.fetchone()

            if result:
                self.test_user_id, self.test_offerer_id, count = result
                logger.info(
                    f"Found test entities: user_id={self.test_user_id}, "
                    f"offerer_id={self.test_offerer_id} (with {count} bookings)"
                )

                cursor.execute(
                    """
                    SELECT "venueId"
                    FROM booking
                    WHERE "offererId" = %s
                    LIMIT 1
                    """,
                    (self.test_offerer_id,),
                )
                venue_result = cursor.fetchone()
                if venue_result:
                    self.test_venue_id = venue_result[0]
                    logger.info(f"  venue_id={self.test_venue_id}")
            else:
                logger.error(
                    "No suitable test entities found! Database may not have enough data."
                )
                sys.exit(1)

    def run_query_with_metrics(
        self,
        query: str,
        params: tuple | None = None,
        fetch_results: bool = True,
    ) -> PerformanceMetrics:
        """Execute query and collect performance metrics."""
        metrics = PerformanceMetrics(query_name="query")

        try:
            if not self.conn:
                raise ValueError("Database connection is not established")
            with self.conn.cursor() as cursor:
                mem_before = self.get_memory_usage_mb()
                start_time = time.perf_counter()

                cursor.execute(query, params or ())

                if fetch_results:
                    results = cursor.fetchall()
                    metrics.result_count = len(results)

                end_time = time.perf_counter()
                mem_after = self.get_memory_usage_mb()

                metrics.execution_time_ms = (end_time - start_time) * 1000
                metrics.memory_usage_mb = mem_after - mem_before

        except Exception as e:
            logger.error(f"Query execution error: {e}")
            metrics.error = str(e)

        return metrics

    def benchmark_count_query(self, period_days: int = 30) -> PerformanceMetrics:
        """Benchmark the booking count query (used for pagination)."""
        logger.info(f"Benchmarking count query (last {period_days} days)...")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)

        query = """
            WITH bookings AS (
                SELECT DISTINCT b.id, b.quantity
                FROM booking b
                JOIN offerer o ON b."offererId" = o.id
                JOIN user_offerer uo ON uo."offererId" = o.id
                JOIN stock s ON b."stockId" = s.id
                JOIN offer OF ON s."offerId" = of.id
                WHERE uo."userId" = %s
                    AND uo."validationStatus" = 'VALIDATED'
                    AND b."dateCreated" BETWEEN %s AND %s
                    AND b."offererId" = %s
            )
            SELECT COALESCE(SUM(quantity), 0) as total
            FROM bookings;
        """

        metrics = self.run_query_with_metrics(
            query,
            (self.test_user_id, start_date, end_date, self.test_offerer_id),
            fetch_results=True,
        )
        metrics.query_name = f"count_query_{period_days}d"

        return metrics

    def benchmark_list_query(
        self,
        period_days: int = 30,
        page: int = 1,
        per_page: int = 1000,
    ) -> PerformanceMetrics:
        """Benchmark the booking list query (main data retrieval)."""
        logger.info(
            f"Benchmarking list query (last {period_days} days, page {page})..."
        )

        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        offset = (page - 1) * per_page

        query = """
            SELECT DISTINCT ON (b.id)
                b.token as "bookingToken",
                b."dateCreated" as "bookedAt",
                b.quantity,
                b.amount as "bookingAmount",
                b."priceCategoryLabel",
                b."dateUsed" as "usedAt",
                b."cancellationDate" as "cancelledAt",
                b."cancellationLimitDate",
                b.status,
                b."reimbursementDate" as "reimbursedAt",
                of.name as "offerName",
                of.id as "offerId",
                of.ean as "offerEan",
                u."firstName" as "beneficiaryFirstname",
                u."lastName" as "beneficiaryLastname",
                u.email as "beneficiaryEmail",
                u."phoneNumber" as "beneficiaryPhoneNumber",
                s."beginningDatetime" as "stockBeginningDatetime",
                b."stockId"
            FROM booking b
            JOIN offerer o ON b."offererId" = o.id
            JOIN user_offerer uo ON uo."offererId" = o.id
            JOIN stock s ON b."stockId" = s.id
            JOIN offer of ON s."offerId" = of.id
            JOIN "user" u ON b."userId" = u.id
            WHERE uo."userId" = %s
                AND uo."validationStatus" = 'VALIDATED'
                AND b."dateCreated" BETWEEN %s AND %s
                AND b."offererId" = %s
            ORDER BY b.id, b."dateCreated" DESC
            LIMIT %s OFFSET %s;
        """

        metrics = self.run_query_with_metrics(
            query,
            (
                self.test_user_id,
                start_date,
                end_date,
                self.test_offerer_id,
                per_page,
                offset,
            ),
            fetch_results=True,
        )
        metrics.query_name = f"list_query_{period_days}d_page{page}"

        return metrics

    def benchmark_status_filter_query(
        self, status: str, period_days: int = 90
    ) -> PerformanceMetrics:
        """Benchmark query with status filter."""
        logger.info(
            f"Benchmarking status filter query (status={status}, last {period_days} days)..."
        )

        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)

        query = """
            SELECT COUNT(DISTINCT b.id)
            FROM booking b
            JOIN offerer o ON b."offererId" = o.id
            JOIN user_offerer uo ON uo."offererId" = o.id
            WHERE uo."userId" = %s
                AND uo."validationStatus" = 'VALIDATED'
                AND b."dateCreated" BETWEEN %s AND %s
                AND b.status = %s;
        """

        metrics = self.run_query_with_metrics(
            query,
            (self.test_user_id, start_date, end_date, status),
            fetch_results=True,
        )
        metrics.query_name = f"status_filter_{status}_{period_days}d"

        return metrics

    def benchmark_venue_filter_query(self, period_days: int = 60) -> PerformanceMetrics:
        """Benchmark query with venue filter."""
        logger.info(f"Benchmarking venue filter query (last {period_days} days)...")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)

        query = """
            SELECT COUNT(DISTINCT b.id)
            FROM booking b
            JOIN offerer o ON b."offererId" = o.id
            JOIN user_offerer uo ON uo."offererId" = o.id
            WHERE uo."userId" = %s
                AND uo."validationStatus" = 'VALIDATED'
                AND b."dateCreated" BETWEEN %s AND %s
                AND b."venueId" = %s;
        """

        metrics = self.run_query_with_metrics(
            query,
            (self.test_user_id, start_date, end_date, self.test_venue_id),
            fetch_results=True,
        )
        metrics.query_name = f"venue_filter_{period_days}d"

        return metrics

    def run_full_benchmark_suite(self) -> list[PerformanceMetrics]:
        """Run complete benchmark suite."""
        logger.info("=" * 80)
        logger.info("Starting Full Benchmark Suite")
        logger.info("=" * 80)

        results = []

        test_scenarios = [
            ("count_query", lambda: self.benchmark_count_query(30)),
            ("count_query", lambda: self.benchmark_count_query(90)),
            ("count_query", lambda: self.benchmark_count_query(365)),
            ("count_query", lambda: self.benchmark_count_query(1095)),
            ("list_query", lambda: self.benchmark_list_query(30, page=1)),
            ("list_query", lambda: self.benchmark_list_query(90, page=1)),
            ("list_query", lambda: self.benchmark_list_query(365, page=1)),
            ("list_query", lambda: self.benchmark_list_query(1095, page=1)),
            ("list_query", lambda: self.benchmark_list_query(30, page=5)),
            (
                "status_filter",
                lambda: self.benchmark_status_filter_query("CONFIRMED", 90),
            ),
            ("status_filter", lambda: self.benchmark_status_filter_query("USED", 90)),
            (
                "status_filter",
                lambda: self.benchmark_status_filter_query("CANCELLED", 90),
            ),
            ("venue_filter", lambda: self.benchmark_venue_filter_query(60)),
        ]

        for scenario_name, scenario_func in test_scenarios:
            try:
                metrics = scenario_func()
                results.append(metrics)
                logger.info(
                    f"  → {metrics.query_name}: {metrics.execution_time_ms:.2f}ms, "
                    f"{metrics.result_count} results, {metrics.memory_usage_mb:.2f}MB"
                )
            except Exception as e:
                logger.error(f"  → {scenario_name}: ERROR - {e}")

        self.results = results
        return results


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark booking queries performance"
    )
    parser.add_argument(
        "--service",
        choices=["postgres", "timescaledb"],
        required=True,
        help="Which database to benchmark",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output JSON file path for results",
    )
    parser.add_argument(
        "--runs",
        type=int,
        required=True,
        help="Number of runs for each query",
    )
    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("Booking Queries Performance Benchmark")
    logger.info(f"Service: `{args.service}`")
    logger.info(f"Output: `{args.output}`")
    logger.info(f"Runs per query: `{args.runs}`")
    logger.info("=" * 80)

    all_results = []

    for run in range(1, args.runs + 1):
        logger.info(f"\n{'-' * 80}")
        logger.info(f"RUN {run}/{args.runs}")
        logger.info(f"{'-' * 80}")

        benchmark = BookingQueryBenchmark(
            service=args.service,
        )

        try:
            benchmark.connect()
            benchmark.find_test_entities()

            if run == 1:
                disk_sizes = benchmark.get_disk_sizes()
                logger.info(
                    f"Disk usage: {disk_sizes['total_size_pretty']} "
                    f"(table: {disk_sizes['table_size_pretty']}, "
                    f"indexes: {disk_sizes['indexes_size_pretty']})"
                )
                if disk_sizes["compression_stats"]:
                    comp = disk_sizes["compression_stats"]
                    logger.info(
                        f"Compression: {comp['compressed_chunks']}/{comp['total_chunks']} chunks compressed, "
                        f"ratio: {comp['compression_ratio']}x"
                    )

            results = benchmark.run_full_benchmark_suite()

            for result in results:
                result_dict = result.to_dict()
                result_dict["run"] = run
                result_dict["service"] = args.service
                all_results.append(result_dict)

        except Exception as e:
            logger.error(f"Benchmark error: {e}", exc_info=True)
            sys.exit(1)
        finally:
            benchmark.disconnect()

    benchmark_final = BookingQueryBenchmark(
        service=args.service,
    )
    benchmark_final.connect()
    disk_sizes = benchmark_final.get_disk_sizes()
    benchmark_final.disconnect()

    output_data = {
        "metadata": {
            "service": args.service,
            "runs": args.runs,
            "timestamp": datetime.now().isoformat(),
            "disk_usage": disk_sizes,
        },
        "results": all_results,
    }

    with open(args.output, "w") as f:
        json.dump(output_data, f, indent=2, default=str)

    logger.info(f"\n{'-' * 80}")
    logger.info(f"Benchmark Done. Results saved to: `{args.output}`.")
    logger.info(f"{'-' * 80}")


if __name__ == "__main__":
    main()
