import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest
from prometheus_client import CollectorRegistry
from prometheus_client import Counter
from prometheus_client import Gauge
from prometheus_client import Histogram
from prometheus_client import multiprocess
from prometheus_client import values


@pytest.fixture
def gunicorn_config(monkeypatch, tmp_path):
    monkeypatch.setenv("ENABLE_FLASK_PROMETHEUS_EXPORTER", "1")
    monkeypatch.setenv("PROMETHEUS_MULTIPROC_DIR", str(tmp_path))
    monkeypatch.setenv("GUNICORN_WORKER_TYPE", "gthread")
    config_path = Path(__file__).resolve().parents[1] / "gunicorn.conf.py"
    spec = importlib.util.spec_from_file_location("gunicorn_config", config_path)
    assert spec is not None and spec.loader is not None
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return config


@pytest.fixture
def worker_metrics(monkeypatch, tmp_path):
    """Use synthetic worker PIDs with the client's real mmap writer and collector."""
    monkeypatch.setenv("PROMETHEUS_MULTIPROC_DIR", str(tmp_path))
    for pid, requests, duration, threads in ((123, 2, 0.5, 2), (456, 3, 1.0, 3)):
        monkeypatch.setattr(values, "ValueClass", values.MultiProcessValue(process_identifier=lambda pid=pid: pid))
        Counter("test_http_requests", "HTTP requests", registry=None).inc(requests)
        Histogram("test_http_duration_seconds", "HTTP duration", registry=None).observe(duration)
        Gauge("test_worker_threads", "Worker capacity", multiprocess_mode="livesum", registry=None).set(threads)

    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry, path=str(tmp_path))
    return registry


@pytest.mark.parametrize("hook_name", ["child_exit", "worker_exit"])
def test_worker_exit_preserves_cumulative_metrics(gunicorn_config, worker_metrics, tmp_path, hook_name):
    """Worker recycling must not erase HTTP history or retain dead worker capacity."""
    assert worker_metrics.get_sample_value("test_http_requests_total") == 5
    assert worker_metrics.get_sample_value("test_http_duration_seconds_count") == 2
    assert worker_metrics.get_sample_value("test_http_duration_seconds_sum") == 1.5
    assert worker_metrics.get_sample_value("test_worker_threads") == 5
    other_worker_files = set(tmp_path.glob("*_456.db"))

    hook = getattr(gunicorn_config, hook_name)
    hook(None, SimpleNamespace(pid=123))
    hook(None, SimpleNamespace(pid=123))

    assert worker_metrics.get_sample_value("test_http_requests_total") == 5
    assert worker_metrics.get_sample_value("test_http_duration_seconds_count") == 2
    assert worker_metrics.get_sample_value("test_http_duration_seconds_sum") == 1.5
    assert worker_metrics.get_sample_value("test_http_duration_seconds_bucket", {"le": "0.5"}) == 1
    assert worker_metrics.get_sample_value("test_http_duration_seconds_bucket", {"le": "+Inf"}) == 2
    assert worker_metrics.get_sample_value("test_worker_threads") == 3
    assert set(tmp_path.glob("*_456.db")) == other_worker_files


@pytest.mark.parametrize("hook_name", ["child_exit", "worker_exit"])
def test_worker_exit_without_metrics(gunicorn_config, worker_metrics, monkeypatch, tmp_path, hook_name):
    monkeypatch.setattr(gunicorn_config, "ENABLE_FLASK_PROMETHEUS_EXPORTER", 0)
    existing_files = set(tmp_path.iterdir())

    getattr(gunicorn_config, hook_name)(None, SimpleNamespace(pid=123))

    assert set(tmp_path.iterdir()) == existing_files
    assert worker_metrics.get_sample_value("test_http_requests_total") == 5
    assert worker_metrics.get_sample_value("test_worker_threads") == 5
