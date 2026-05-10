import os
import logging

logger = logging.getLogger(__name__)

_METRIC_PREFIX = "custom.googleapis.com/security_intelligence"

RUNS_STARTED = f"{_METRIC_PREFIX}/runs_started"
RUNS_COMPLETED = f"{_METRIC_PREFIX}/runs_completed"
RUNS_FAILED = f"{_METRIC_PREFIX}/runs_failed"
TOOL_CALLS_TOTAL = f"{_METRIC_PREFIX}/tool_calls_total"


def increment(metric_name: str, project_id: str, labels: dict | None = None) -> None:
    """Increment a custom Cloud Monitoring counter metric by 1."""
    try:
        from google.cloud import monitoring_v3
        import time

        client = monitoring_v3.MetricServiceClient()
        project_name = f"projects/{project_id}"

        series = monitoring_v3.TimeSeries()
        series.metric.type = metric_name
        if labels:
            series.metric.labels.update(labels)

        series.resource.type = "global"
        series.resource.labels["project_id"] = project_id

        now = time.time()
        seconds = int(now)
        nanos = int((now - seconds) * 10**9)
        interval = monitoring_v3.TimeInterval(
            {"end_time": {"seconds": seconds, "nanos": nanos}}
        )
        point = monitoring_v3.Point(
            {"interval": interval, "value": {"int64_value": 1}}
        )
        series.points = [point]

        client.create_time_series(name=project_name, time_series=[series])

    except Exception as e:
        # Metrics must never crash the pipeline — log and continue
        logger.warning("Failed to emit metric %s: %s", metric_name, e)
