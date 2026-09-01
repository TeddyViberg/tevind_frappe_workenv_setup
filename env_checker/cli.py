import sys

from env_checker.models import CheckResult, Status


STATUS_SYMBOLS = {
    Status.OK: "✓",
    Status.MISSING: "✗",
    Status.OUTDATED: "!",
    Status.WARN: "?",
}


def print_report(results: list[CheckResult]) -> int:
    ok_count = sum(1 for r in results if r.passed)
    total = len(results)

    print(f"\n{'Dependency':<20} {'Required':<28} {'Installed':<16} {'Status'}")
    print("-" * 80)

    for result in results:
        symbol = STATUS_SYMBOLS.get(result.status, "?")
        print(
            f"{result.name:<20} {result.required:<28} {result.installed:<16} "
            f"{symbol} {result.status.label}"
        )
        if result.hint and result.status != Status.OK:
            print(f"  → {result.hint}")

    print("-" * 80)
    issues = total - ok_count
    if issues == 0:
        print(f"All {total} checks passed.")
    else:
        print(f"{ok_count}/{total} passed — {issues} issue(s).")

    return 0 if issues == 0 else 1


def main(results: list[CheckResult]) -> None:
    sys.exit(print_report(results))
