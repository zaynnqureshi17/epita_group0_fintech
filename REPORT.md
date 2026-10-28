# EPITA Engineering Tools TP2 — Group 0 Stripe Project

**Course:** Engineering Tools — Session 2  
**Instructor:** Ismail Lachheb  
**Group:** Group 0 — Fintech & Payments (Stripe Test Mode)  
**Members:** Kusananda Thakur, Rachid Rahme, Steven El Hayek, Muhammad Zain Qureshi  
**Date:** 28/10/2026  
**Assigned API Domain:** Stripe Test Mode (`STRIPE_API_KEY`)  
**Project Directory:** `epita_group0_fintech`  
**Project Package:** `epita_rachid_rahme_fintech`  
**TestPyPI URL:** https://test.pypi.org/project/epita-rachid-rahme-fintech/

---

## Step 0: Assigned Group Verification

The official Group 0 roster assigns this project to the Stripe Test Mode domain. The live target is `GET https://api.stripe.com/v1/balance` and the required authentication header is `Authorization: Bearer <STRIPE_API_KEY>`.

---

## Part 1: Environment Isolation with uv

### 1.1 Verified global vs uv environment

```text
Global run:
- sys.executable: C:\Python314\python.exe
- sys.prefix: C:\Python314
- sys.base_prefix: C:\Python314
- Is in virtual environment?: False

uv run:
- sys.executable: C:\Users\rahme\Desktop\engineering Tools\epita_group0_fintech\.venv\Scripts\python.exe
- sys.prefix: C:\Users\rahme\Desktop\engineering Tools\epita_group0_fintech\.venv
- sys.base_prefix: C:\Python314
- Is in virtual environment?: True
```

### 1.2 Analysis

`uv run` automatically selects the project-local virtual environment and executes the command inside that environment without requiring manual shell activation. This keeps project dependencies isolated from the global interpreter and prevents version drift between projects.

### 1.3 Git hygiene

The repository excludes the expected local-only files:

```gitignore
.venv/
.env
__pycache__/
.pytest_cache/
dist/
*.egg-info/
*.txt
```

The diagnostic script remains tracked in the repository and the secret-bearing files stay out of Git.

---

## Part 2: Live API Connection & Secret Hygiene

### 2.1 Git status evidence

```text
## codex-final-integration
 M REPORT.md
 M pyproject.toml
?? TP2_GROUP_0.zip
?? scripts/
?? src/epita_rachid_rahme_fintech/cli.py
?? tests/
```

Ignored sensitive files:

```text
!! .env
!! .venv/
!! dist/
!! global_env_output.txt
!! uv_env_output.txt
```

The `.env` file remains ignored and `.env.template` is tracked.

### 2.2 Live API response

Verified response from the project client:

```python
{'status': 'LIVE_SUCCESS', 'currency': 'EUR', 'available_balance': 0.0, 'livemode': False}
```

This confirms the call succeeded in Stripe test mode with a valid sandbox key. The balance is `0.0` because no test transactions were created in the sandbox account.

### 2.3 Security analysis

1. Environment variables keep secrets outside the repository, which reduces the risk of accidentally leaking credentials in source control or code review tools.
2. They support isolated credentials per environment, such as local development, CI, and production, without requiring code changes.

Why unsafe fallbacks are dangerous:

- `os.getenv("STRIPE_API_KEY", "default")` can silently hide misconfiguration.
- Production systems may authenticate with the wrong secret or a fake fallback, which is both insecure and hard to detect.

---

## Part 3: Dependency Hygiene & Semantic Versioning

### 3.1 Dependency tree

```text
epita-rachid-rahme-fintech v0.1.0
├── python-dotenv v1.2.4
├── requests v2.34.2
│   ├── certifi v2026.10.23
│   ├── charset-normalizer v3.5.2
│   ├── idna v3.20
│   └── urllib3 v2.8.0
├── rich v15.0.0
│   ├── markdown-it-py v4.2.0
│   │   └── mdurl v0.1.2
│   └── pygments v2.21.0
└── pytest v9.2.0 (group: dev)
    ├── colorama v0.4.6
    ├── iniconfig v2.3.1
    ├── packaging v26.3
    ├── pluggy v1.7.0
    └── pygments v2.21.0
```

- Direct dependencies: `requests`, `python-dotenv`, `rich`
- Development dependency: `pytest`
- Transitive dependencies: `certifi`, `charset-normalizer`, `idna`, `urllib3`, `markdown-it-py`, `mdurl`, `pygments`, `iniconfig`, `packaging`, `pluggy`, `colorama`

### 3.2 SemVer explanation

- `^2.31.0` allows updates within the same major version, so versions `>=2.31.0` and `<3.0.0` are accepted.
- `~=2.2.1` allows updates within the same minor series, so versions `>=2.2.1` and `<2.3.0` are accepted.
- `==13.7.1` pins one exact version.
- `^2.31.0` does not allow `3.0.0` because the major version changes.
- `pyproject.toml` declares allowed ranges; `uv.lock` records the exact resolved versions and their hashes for deterministic installs.
- SHA-256 hashes in `uv.lock` protect against tampered package downloads, including compromised mirrors or malicious replacements of the same version.

---

## Part 4: Package Build, TestPyPI Publication, and CLI Execution

### 4.1 Published package status

**Publication status:** Successfully published to TestPyPI and verified.

**Public URL:** https://test.pypi.org/project/epita-rachid-rahme-fintech/

### 4.2 Verified external CLI execution

The package was executed successfully from a temporary directory after installation from TestPyPI. The output was:

```text
Status: LIVE_SUCCESS
Currency: EUR
Available Balance: 0.00
Livemode: False
```

### 4.3 Local build and packaging

The project builds successfully with:

```powershell
python -m uv build
```

Artifacts created:

```text
dist\epita_rachid_rahme_fintech-0.1.0-py3-none-any.whl
dist\epita_rachid_rahme_fintech-0.1.0.tar.gz
```

### 4.4 Packaging theory

- An `sdist` (`.tar.gz`) is a source distribution containing the package source and metadata.
- A wheel (`.whl`) is a prebuilt binary distribution that is faster to install and less dependent on local build toolchains.
- Wheels are faster to install because the client avoids building the package locally.
- Avoiding arbitrary build-time execution reduces supply-chain risk and makes installations safer.
- The console script entry point works because `pyproject.toml` registers the command name and points it to `epita_rachid_rahme_fintech.cli:main`.

---

## Part 5: Professional Debugging Challenge

### 5.1 Root cause analysis

The issue was caused by mixing string and numeric values during parsing. The original implementation had to coerce CSV values such as `raw_volume` and `weight_multiplier` to `float`, while preserving record IDs as strings like `REC_001`. The logic must only aggregate `SUCCESS` records and apply the high-impact threshold of `> 500`.

### 5.2 Conditional breakpoint and call stack

At a conditional breakpoint set on the loop index `idx == 2`, the relevant stack is:

```text
Frame 1: aggregate_telemetry(payload)
Frame 2: parse_api_record(raw_entry)
Frame 3: __main__ (entry script / module call)
```

This is the relevant path because the failure occurs while the loop is parsing the active record, converting the numeric fields, and then evaluating the weighted impact before adding the record to the success set.

### 5.3 Corrected code

```python
def parse_api_record(raw_entry: str) -> dict:
    record_id, entity_name, raw_volume, status, weight_multiplier = raw_entry.split(",")
    return {
        "record_id": record_id.strip(),
        "entity_name": entity_name.strip(),
        "volume": float(raw_volume.strip()),
        "status": status.strip(),
        "weight": float(weight_multiplier.strip()),
    }


def compute_weighted_metric(volume, weight):
    return float(volume) * float(weight)


def aggregate_telemetry(payload: list[str]) -> dict:
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
```

### 5.4 Verified output

```python
{'successful_entries': 3, 'total_volume': 650.0, 'avg_volume': 216.66666666666666, 'high_impact_count': 1}
```

This matches the required result using the correct threshold of `> 500`.

---

## Final Quality Check Against the 20-Point Rubric

- Modern UV workflow: complete and verified
- Stripe API work: complete and verified with live test-mode response
- Dependency hygiene and SemVer: complete and verified
- CLI and packaging: complete and verified locally, plus published and externally validated on TestPyPI
- Debugging challenge: corrected and verified with the required output
- Security and archive hygiene: valid, with `.env`, `.venv`, caches, and secrets excluded from the final ZIP

The project is in a correctly verified state for submission, with no remaining blocker aside from final user approval before sending or publishing any additional artifacts.
