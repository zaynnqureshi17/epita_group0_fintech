from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from epita_rachid_rahme_fintech.client import fetch_live_data

console = Console()


def main() -> int:
    try:
        data = fetch_live_data()
    except Exception as exc:  # pragma: no cover - CLI error path is verified by execution output
        console.print(
            Panel(
                f"[bold red]Stripe request failed[/bold red]\n{exc}",
                title="API Error",
                border_style="red",
            )
        )
        raise SystemExit(1) from exc

    table = Table(title="Group 0 — Stripe Test Mode Dashboard", header_style="bold cyan")
    table.add_column("Field", style="bold")
    table.add_column("Value")
    table.add_row("Status", str(data.get("status", "UNKNOWN")))
    table.add_row("Currency", str(data.get("currency", "N/A")))
    table.add_row("Available Balance", f"{float(data.get('available_balance', 0.0)):.2f}")
    table.add_row("Livemode", "True" if data.get("livemode") else "False")

    console.print(
        Panel(
            table,
            title="EPITA Fintech & Payments",
            subtitle="Stripe sandbox data (secret key omitted)",
            border_style="green",
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
