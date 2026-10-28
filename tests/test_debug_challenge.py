import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "debug_challenge.py"
SPEC = importlib.util.spec_from_file_location("debug_challenge", MODULE_PATH)
DEBUG_MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DEBUG_MODULE)
aggregate_telemetry = DEBUG_MODULE.aggregate_telemetry


def test_debug_challenge_uses_string_record_ids_and_500_threshold():
    payload = [
        "REC_001,alpha,120.0,SUCCESS,0.5",
        "REC_002,beta,200.0,FAIL,2.0",
        "REC_003,gamma,180.0,SUCCESS,0.2",
        "REC_004,delta,350.0,SUCCESS,1.5",
    ]

    result = aggregate_telemetry(payload)

    assert result == {
        "successful_entries": 3,
        "total_volume": 650.0,
        "avg_volume": 216.66666666666666,
        "high_impact_count": 1,
    }
