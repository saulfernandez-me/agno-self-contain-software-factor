import time

from apf_core.workflow import ApfWorkflow


def test_apf_workflow_initialization() -> None:
    """Test that the ApfWorkflow initializes correctly with tracking dicts."""
    workflow = ApfWorkflow(name="test_workflow")

    assert workflow.name == "test_workflow"
    assert "agent" in workflow.lane_metrics
    assert "code" in workflow.lane_metrics
    assert "engineer" in workflow.lane_metrics

    for lane_type in ["agent", "code", "engineer"]:
        assert workflow.lane_metrics[lane_type]["count"] == 0  # type: ignore
        assert workflow.lane_metrics[lane_type]["total_time_ms"] == 0.0  # type: ignore


def test_apf_workflow_lane_tracking() -> None:
    """Test that the lane context manager accurately tracks count and time."""
    workflow = ApfWorkflow(name="test_tracking")

    # Execute an 'agent' lane
    with workflow.lane("agent"):
        time.sleep(0.01)  # Simulate 10ms of work

    # Execute a 'code' lane
    with workflow.lane("code"):
        time.sleep(0.02)  # Simulate 20ms of work

    metrics = workflow.lane_metrics

    # Verify agent lane
    assert metrics["agent"]["count"] == 1
    assert metrics["agent"]["total_time_ms"] >= 10.0

    # Verify code lane
    assert metrics["code"]["count"] == 1
    assert metrics["code"]["total_time_ms"] >= 20.0

    # Verify engineer lane remained untouched
    assert metrics["engineer"]["count"] == 0
    assert metrics["engineer"]["total_time_ms"] == 0.0


def test_apf_workflow_lane_exception_handling() -> None:
    """Test that the lane context manager tracks metrics even if an exception occurs."""
    workflow = ApfWorkflow(name="test_exception")

    try:
        with workflow.lane("code"):
            time.sleep(0.01)
            raise ValueError("Intentional crash")
    except ValueError:
        pass

    assert workflow.lane_metrics["code"]["count"] == 1
    assert workflow.lane_metrics["code"]["total_time_ms"] > 0
