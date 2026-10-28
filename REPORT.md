# EPITA — Engineering Tools TP2 Report

**Course:** Engineering Tools — Session 2  
**Group:** 0 — Fintech & Payments (Stripe Test Mode)  
**Project:** epita_group0_fintech  
**Python package:** epita-rachid-rahme-fintech  
**Version:** 0.1.0

---

## Part 1 — Modern Environment Isolation with uv

### 1.1 Installing uv

We installed uv using pip:

```powershell
pip install uv
```

We verified the installation using:

```powershell
python -m uv --version
```

Result:

```text
uv 0.13.6
```

The direct `uv` command was initially not recognized by PowerShell because its executable directory was not available on PATH. We successfully used `python -m uv` instead.

### 1.2 Project Initialization

We initialized our Python library project using:

```powershell
python -m uv init --lib --name epita_rachid_rahme_fintech
```

The project contains `pyproject.toml`, `.python-version`, and a Python package under `src/`.

### 1.3 Virtual Environment

We created the virtual environment using:

```powershell
python -m uv venv
```

Result:

```text
Using CPython 3.14.3 interpreter
Creating virtual environment at: .venv
```

**What is the difference between sys.executable and sys.prefix?**

- `sys.executable` gives the path of the Python interpreter being used.
- `sys.prefix` identifies the current Python installation or virtual environment.

When Python runs globally, these values refer to the global Python installation. When Python runs inside the uv-managed environment, both refer to the isolated environment.

**How does uv run isolate the environment?**

`uv run` automatically uses the project's managed virtual environment. It ensures the project dependencies are available without requiring manual activation of `.venv`.

**Environment comparison:** Actual output from `global_env_output.txt` and `uv_env_output.txt` will be added after running the required diagnostic script.

### 1.4 Git Hygiene

The `.gitignore` file protects local environment files and temporary artifacts.

Excluded files include:

```gitignore
.venv/
.env
__pycache__/
.pytest_cache/
dist/
*.egg-info/
*.txt
```

This prevents virtual environments, credentials, build artifacts, and temporary output files from being committed to Git.

---

## Part 2 — Live Stripe API Integration

**Assigned API provider:** Stripe Test Mode

**Environment variable:** `STRIPE_API_KEY`

**HTTP endpoint:**

```text
GET https://api.stripe.com/v1/balance
```

**Authentication:**

```text
Authorization: Bearer <STRIPE_API_KEY>
```

### 2.1 Dependencies

We installed:

```powershell
python -m uv add requests python-dotenv
```

- `requests` handles HTTP requests to the Stripe REST API.
- `python-dotenv` loads private environment variables from `.env`.

### 2.2 Secure Configuration

The real Stripe test API key is stored locally in `.env`, which is excluded from Git.

The public `.env.template` contains placeholders and can be committed safely.

**Why should API keys be stored in environment variables?**

1. **Security:** Secrets are separated from source code, reducing the risk of accidentally publishing credentials in a repository.
2. **Flexibility:** Different environments can use different credentials without changing application code.

### 2.3 Live API Response

`config.py` loads `.env` with `python-dotenv` and reads `STRIPE_API_KEY`. Its `validate()` method raises a `ValueError` before any network call if the key is missing or still the `your_` placeholder:

```text
ValueError: CRITICAL SECURITY / CONFIG ERROR: API key is not configured!
Ensure your .env file exists and contains a valid API key.
```

`client.py` calls `GET /v1/balance` with `Authorization: Bearer <STRIPE_API_KEY>` and returns the first available balance.

Live test (the key is read from `.env` and never printed):

```bash
uv run python -c "from epita_rachid_rahme_fintech.client import fetch_live_data; print(fetch_live_data())"
```

```text
{'status': 'LIVE_SUCCESS', 'currency': 'EUR', 'available_balance': 0.0, 'livemode': False}
```

`livemode: False` confirms the request used a Stripe test key (`sk_test_****`). The balance is 0.0 EUR because the sandbox account has no test payments.

### 2.4 Git Status

`git status` after staging the Part 2 files, with `.env` present on disk containing the real key:

```text
$ git status
On branch part2-stripe-api
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
	modified:   REPORT.md
	new file:   src/epita_rachid_rahme_fintech/client.py
	new file:   src/epita_rachid_rahme_fintech/config.py
```

`.env` does not appear, even as untracked. Git confirms it is ignored and that `.env.template` is tracked:

```text
$ git status --short --ignored
!! .env
!! .venv/
$ git check-ignore -v .env
.gitignore:2:.env	.env
$ git ls-files .env.template .env
.env.template
```

---

## Part 3 — Dependency Locking and Semantic Versioning

### 3.1 Installed Dependencies

We added the required project dependencies:

```powershell
python -m uv add requests python-dotenv rich
python -m uv add --dev pytest
```

- `requests`: HTTP communication
- `python-dotenv`: Environment configuration
- `rich`: Styled terminal output
- `pytest`: Development and testing

### 3.2 Dependency Tree

We executed:

```powershell
python -m uv tree
```

Output:

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

**Direct dependencies** (declared in `pyproject.toml`): `requests`, `python-dotenv`, `rich`.

**Development dependency** (`[dependency-groups] dev`, not shipped with the package): `pytest`.

**Transitive dependencies:**

| Pulled in by | Transitive dependencies |
|---|---|
| `requests` | `certifi`, `charset-normalizer`, `idna`, `urllib3` |
| `rich` | `markdown-it-py` (which itself pulls in `mdurl`), `pygments` |
| `pytest` (dev) | `iniconfig`, `packaging`, `pluggy`, `pygments`, `colorama` (Windows only) |

`pygments` is needed by both `rich` and `pytest`, but it is installed only once.

`colorama` appears in the tree above, which was run on Windows, but not when `uv tree` runs on Linux. In `uv.lock`, pytest declares it with a platform marker: `{ name = "colorama", marker = "sys_platform == 'win32'" }`. The lockfile is universal: it resolves every platform once, and each machine installs only what applies to it.

### 3.3 Why Does uv.lock Contain SHA-256 Hashes?

Every file uv may download is listed in `uv.lock` with its exact URL and its SHA-256 hash, for example:

```text
sdist = { url = "https://files.pythonhosted.org/.../colorama-0.4.6.tar.gz", hash = "sha256:08695f5cb7ed6e0531a20572697297273c47b8cae5a63ffc6d6ed5c201be6e44" }
```

During `uv sync`, uv computes the hash of each downloaded file and refuses to install it if it differs from the hash in the lockfile. Any of these makes the hash differ, so the attack fails at install time instead of running on our machines:

- a compromised mirror or package index;
- a man-in-the-middle;
- an attacker replacing a release file under the same version number.

Every machine in the group therefore installs byte-for-byte the same files that were locked.

The hash only proves the file has not changed since it was locked. It does not protect against a version that was already malicious when we locked it, so changes to `uv.lock` still need to be reviewed.

### 3.4 Semantic Versioning

**requests = "^2.31.0"**

Allows compatible releases from version 2.31.0 up to, but excluding, 3.0.0.

**urllib3 = "~=2.2.1"**

Allows versions from 2.2.1 up to, but excluding, 2.3.0.

**rich = "==13.7.1"**

Requires exactly version 13.7.1.

| Constraint | Range | Updates allowed |
|---|---|---|
| `^2.31.0` | `>=2.31.0, <3.0.0` | minor and patch |
| `~=2.2.1` | `>=2.2.1, <2.3.0` | patch only |
| `==13.7.1` | `13.7.1` only | none |

The caret `^` is Poetry and npm syntax. It is not valid in a standard (PEP 621) `pyproject.toml` read by uv, where the same range is written `requests>=2.31.0,<3`.

### 3.5 Would uv lock --upgrade Install Version 3.0.0?

No. `uv lock --upgrade` picks the newest version allowed by the constraint, so with `^2.31.0` it moves to the newest 2.x release and stops there. The upper bound `<3.0.0` excludes 3.0.0.

Under SemVer (MAJOR.MINOR.PATCH), a new MAJOR version signals breaking changes, and the caret exists to accept only non-breaking updates. Moving to 3.x requires changing the constraint in `pyproject.toml` on purpose, after checking the breaking changes.

### 3.6 Difference Between pyproject.toml and uv.lock

| | `pyproject.toml` (declaration) | `uv.lock` (pinning) |
|---|---|---|
| Written by | the developer | generated by uv (`uv add`, `uv lock`) |
| Contains | direct dependencies only | every package, direct and transitive |
| Versions | allowed ranges (`>=2.34.2`) | one exact version each (`2.34.2`) |
| Also stores | project metadata, scripts, build system | source URL and SHA-256 hash of every file |
| Purpose | what the project accepts | the exact environment, identical on every machine |

`pyproject.toml` says what we accept, and `uv.lock` records what we actually got. Both are committed to Git, so `uv sync` rebuilds the same environment for every group member.

---

## Part 4 — Building and Deploying to TestPyPI

Pending implementation of the CLI entry point, package build, TestPyPI publication, and installation verification.

---

## Part 5 — Professional Debugging

Pending debugger investigation, code correction, and validation.

---

## Conclusion

The uv project environment and dependency setup have been completed successfully. The project is ready for Stripe API integration, CLI development, package publishing, and debugging validation.

**Report status:** Work in progress — remaining sections will be completed after integration and testing.