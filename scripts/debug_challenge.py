"""EPITA CM2 debugging challenge: fix the payload parsing and aggregation bug."""


def parse_api_record(raw_entry: str) -> dict:
    """Parse a CSV-like telemetry record while preserving record IDs as strings."""
    record_id, entity_name, raw_volume, status, weight_multiplier = raw_entry.split(",")
    return {
        "record_id": record_id.strip(),
        "entity_name": entity_name.strip(),
        "volume": float(raw_volume.strip()),
        "status": status.strip(),
        "weight": float(weight_multiplier.strip()),
    }


def compute_weighted_metric(volume, weight):
    """Apply the numeric weighting to the record volume."""
    return float(volume) * float(weight)


def aggregate_telemetry(payload: list[str]) -> dict:
    """Aggregate only successful records and compute summary metrics."""
    successful_records = []

    for record_data in payload:
        record = parse_api_record(record_data)
        if record["status"] != "SUCCESS":
            continue

        record["weighted_impact"] = compute_weighted_metric(record["volume"], record["weight"])
        successful_records.append(record)

    total_volume = sum(record["volume"] for record in successful_records)
    successful_count = len(successful_records)
    avg_volume = total_volume / successful_count if successful_count else 0.0
    high_impact_count = sum(1 for record in successful_records if record["weighted_impact"] > 500)

    return {
        "successful_entries": successful_count,
        "total_volume": total_volume,
        "avg_volume": avg_volume,
        "high_impact_count": high_impact_count,
    }


if __name__ == "__main__":
    sample_payload = [
        "REC_001,alpha,120.0,SUCCESS,0.5",
        "REC_002,beta,200.0,FAIL,2.0",
        "REC_003,gamma,180.0,SUCCESS,0.2",
        "REC_004,delta,350.0,SUCCESS,1.5",
    ]
    print(aggregate_telemetry(sample_payload))
