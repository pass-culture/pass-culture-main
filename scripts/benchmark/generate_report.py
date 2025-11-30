"""
Benchmark Results Comparison and Report Generator

Compares benchmark results from multiple JSON files and generates a human-readable Markdown report.

Usage:
    python ./scripts/benchmark/generate_report.py \
        --baseline ./results/baseline.json \
        --compare ./results/timescaledb_hypertable.json ./results/timescaledb_compression.json \
        --output ./results/report.md
"""

import argparse
import json
import logging
import statistics
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def load_benchmark_results(file_path: str) -> dict[str, Any]:
    """Load benchmark results from a JSON file."""
    with open(file_path, "r") as f:
        return json.load(f)


def aggregate_results(results: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    """Aggregate results by query name, computing mean, median, min, max, and stddev."""
    aggregated: dict[str, list[float]] = {}

    for result in results:
        query_name = result["query_name"]
        execution_time = result["execution_time_ms"]

        if query_name not in aggregated:
            aggregated[query_name] = []
        aggregated[query_name].append(execution_time)

    stats: dict[str, dict[str, float]] = {}
    for query_name, times in aggregated.items():
        stats[query_name] = {
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "min": min(times),
            "max": max(times),
            "stddev": statistics.stdev(times) if len(times) > 1 else 0.0,
            "count": len(times),
        }

    return stats


def format_change(baseline_value: float, compare_value: float) -> str:
    """Format the percentage change between baseline and comparison values."""
    if baseline_value == 0:
        return "N/A"

    change = ((compare_value - baseline_value) / baseline_value) * 100

    if change < -5:
        return f"🟢 {change:+.1f}%"
    elif change > 5:
        return f"🔴 {change:+.1f}%"
    else:
        return f"⚪ {change:+.1f}%"


def format_disk_size(size_bytes: int) -> str:
    """Format disk size in human-readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def generate_report(
    baseline_path: str,
    compare_paths: list[str],
    output_path: str,
) -> str:
    """Generate a Markdown comparison report."""
    baseline_data = load_benchmark_results(baseline_path)
    baseline_stats = aggregate_results(baseline_data["results"])
    baseline_metadata = baseline_data["metadata"]

    compare_data_list = []
    for path in compare_paths:
        data = load_benchmark_results(path)
        compare_data_list.append({
            "path": path,
            "name": Path(path).stem,
            "metadata": data["metadata"],
            "stats": aggregate_results(data["results"]),
        })

    report_lines = []

    report_lines.append("# TimescaleDB Benchmark Report")
    report_lines.append("")
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")

    report_lines.append("## Summary")
    report_lines.append("")
    report_lines.append("This report compares query performance between PostgreSQL (baseline) and TimescaleDB configurations.")
    report_lines.append("")

    report_lines.append("### Legend")
    report_lines.append("")
    report_lines.append("- 🟢 **Faster**: > 5% improvement")
    report_lines.append("- 🔴 **Slower**: > 5% regression")
    report_lines.append("- ⚪ **Similar**: within ±5%")
    report_lines.append("")

    report_lines.append("## Disk Usage")
    report_lines.append("")

    disk_headers = ["Configuration", "Table Size", "Index Size", "Total Size"]
    if any(d["metadata"]["disk_usage"].get("compression_stats") for d in compare_data_list):
        disk_headers.append("Compression Ratio")

    report_lines.append("| " + " | ".join(disk_headers) + " |")
    report_lines.append("| " + " | ".join(["---"] * len(disk_headers)) + " |")

    baseline_disk = baseline_metadata["disk_usage"]
    row = [
        f"**{baseline_metadata['service']}** (baseline)",
        baseline_disk["table_size_pretty"],
        baseline_disk["indexes_size_pretty"],
        baseline_disk["total_size_pretty"],
    ]
    if len(disk_headers) > 4:
        row.append("-")
    report_lines.append("| " + " | ".join(row) + " |")

    for compare in compare_data_list:
        disk = compare["metadata"]["disk_usage"]
        row = [
            f"**{compare['name']}**",
            disk["table_size_pretty"],
            disk["indexes_size_pretty"],
            disk["total_size_pretty"],
        ]
        if len(disk_headers) > 4:
            comp_stats = disk.get("compression_stats")
            if comp_stats and comp_stats.get("compression_ratio"):
                row.append(f"{comp_stats['compression_ratio']}x")
            else:
                row.append("-")
        report_lines.append("| " + " | ".join(row) + " |")

    report_lines.append("")

    report_lines.append("## Query Performance (Mean Execution Time)")
    report_lines.append("")

    perf_headers = ["Query", f"{baseline_metadata['service']} (ms)"]
    for compare in compare_data_list:
        perf_headers.append(f"{compare['name']} (ms)")
        perf_headers.append("Change")

    report_lines.append("| " + " | ".join(perf_headers) + " |")
    report_lines.append("| " + " | ".join(["---"] * len(perf_headers)) + " |")

    all_queries = sorted(baseline_stats.keys())
    for query_name in all_queries:
        baseline_mean = baseline_stats[query_name]["mean"]
        row = [f"`{query_name}`", f"{baseline_mean:.2f}"]

        for compare in compare_data_list:
            if query_name in compare["stats"]:
                compare_mean = compare["stats"][query_name]["mean"]
                row.append(f"{compare_mean:.2f}")
                row.append(format_change(baseline_mean, compare_mean))
            else:
                row.append("-")
                row.append("-")

        report_lines.append("| " + " | ".join(row) + " |")

    report_lines.append("")

    report_lines.append("## Detailed Statistics")
    report_lines.append("")

    for query_name in all_queries:
        report_lines.append(f"### `{query_name}`")
        report_lines.append("")

        detail_headers = ["Configuration", "Mean (ms)", "Median (ms)", "Min (ms)", "Max (ms)", "Std Dev", "Runs"]
        report_lines.append("| " + " | ".join(detail_headers) + " |")
        report_lines.append("| " + " | ".join(["---"] * len(detail_headers)) + " |")

        stats = baseline_stats[query_name]
        row = [
            f"**{baseline_metadata['service']}**",
            f"{stats['mean']:.2f}",
            f"{stats['median']:.2f}",
            f"{stats['min']:.2f}",
            f"{stats['max']:.2f}",
            f"{stats['stddev']:.2f}",
            str(int(stats['count'])),
        ]
        report_lines.append("| " + " | ".join(row) + " |")

        for compare in compare_data_list:
            if query_name in compare["stats"]:
                stats = compare["stats"][query_name]
                row = [
                    f"**{compare['name']}**",
                    f"{stats['mean']:.2f}",
                    f"{stats['median']:.2f}",
                    f"{stats['min']:.2f}",
                    f"{stats['max']:.2f}",
                    f"{stats['stddev']:.2f}",
                    str(int(stats['count'])),
                ]
                report_lines.append("| " + " | ".join(row) + " |")

        report_lines.append("")

    report_lines.append("## Configuration Details")
    report_lines.append("")
    report_lines.append(f"- **Baseline**: {baseline_metadata['service']}")
    report_lines.append(f"- **Runs per query**: {baseline_metadata['runs']}")
    report_lines.append(f"- **Baseline timestamp**: {baseline_metadata['timestamp']}")
    for compare in compare_data_list:
        report_lines.append(f"- **{compare['name']} timestamp**: {compare['metadata']['timestamp']}")
    report_lines.append("")

    report_content = "\n".join(report_lines)

    with open(output_path, "w") as f:
        f.write(report_content)

    return report_content


def main():
    parser = argparse.ArgumentParser(
        description="Generate benchmark comparison report"
    )
    parser.add_argument(
        "--baseline",
        required=True,
        help="Path to baseline benchmark results JSON file",
    )
    parser.add_argument(
        "--compare",
        nargs="+",
        required=True,
        help="Paths to comparison benchmark results JSON files",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output path for the Markdown report",
    )
    args = parser.parse_args()

    for path in [args.baseline] + args.compare:
        if not Path(path).exists():
            logger.error(f"File not found: {path}")
            sys.exit(1)

    logger.info("=" * 80)
    logger.info("Generating Benchmark Comparison Report")
    logger.info("=" * 80)
    logger.info(f"Baseline: {args.baseline}")
    for path in args.compare:
        logger.info(f"Compare: {path}")
    logger.info(f"Output: {args.output}")

    report = generate_report(
        baseline_path=args.baseline,
        compare_paths=args.compare,
        output_path=args.output,
    )

    logger.info("-" * 80)
    logger.info("Report generated successfully!")
    logger.info("-" * 80)

    print("\n" + report)


if __name__ == "__main__":
    main()
