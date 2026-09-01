import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

LogCallback = Callable[[str], None]
DEFAULT_TIMEOUT = 600
SCRIPT_TIMEOUT = 1800
PREFLIGHT_SCRIPT = "scripts/upgrades/preflight.sh"


@dataclass
class InstallResult:
    dependency_id: str
    success: bool
    message: str


def get_dependency(config: dict[str, Any], dep_id: str) -> dict[str, Any] | None:
    for dep in config.get("dependencies", []):
        if dep.get("id") == dep_id:
            return dep
    return None


def script_command(script_path: Path) -> str:
    return f"bash '{script_path}'"


def run_shell_step(
    step: str,
    log: LogCallback,
    timeout: int = DEFAULT_TIMEOUT,
) -> tuple[bool, str]:
    log(f"$ {step}")
    try:
        result = subprocess.run(
            step,
            shell=True,
            executable="/bin/bash",
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.stdout:
            log(result.stdout.rstrip())
        if result.stderr:
            log(result.stderr.rstrip())
        if result.returncode != 0:
            return False, f"Command failed (exit {result.returncode})"
        return True, "OK"
    except subprocess.TimeoutExpired:
        return False, f"Timed out after {timeout}s"
    except OSError as exc:
        return False, str(exc)


def run_preflight(config_dir: Path | None, log: LogCallback) -> bool:
    if config_dir is None:
        return True
    script = (config_dir / PREFLIGHT_SCRIPT).resolve()
    if not script.is_file():
        return True
    log("\n--- Pre-install (apt update) ---")
    ok, message = run_shell_step(script_command(script), log, timeout=DEFAULT_TIMEOUT)
    if not ok:
        log(f"Pre-install failed: {message}")
    return ok


def install_dependency(
    dep_id: str,
    config: dict[str, Any],
    log: LogCallback,
    config_dir: Path | None = None,
) -> InstallResult:
    dep = get_dependency(config, dep_id)
    if not dep:
        return InstallResult(dep_id, False, "Unknown dependency")

    if not dep.get("updatable", True):
        return InstallResult(dep_id, False, "Not updatable automatically")

    name = dep.get("name", dep_id)
    log(f"\n--- Installing {name} ---")

    install_script = dep.get("install_script")
    if install_script and config_dir is not None:
        script = (config_dir / install_script).resolve()
        if not script.is_file():
            return InstallResult(dep_id, False, f"Script not found: {script}")
        ok, message = run_shell_step(script_command(script), log, timeout=SCRIPT_TIMEOUT)
        if not ok:
            return InstallResult(dep_id, False, message)
        return InstallResult(dep_id, True, "Installed successfully")

    steps = dep.get("install_steps", [])
    if not steps:
        return InstallResult(dep_id, False, "No install script configured")

    for step in steps:
        ok, message = run_shell_step(step, log)
        if not ok:
            return InstallResult(dep_id, False, message)

    return InstallResult(dep_id, True, "Installed successfully")


def install_dependencies(
    dep_ids: list[str],
    config: dict[str, Any],
    log: LogCallback,
    config_dir: Path | None = None,
) -> list[InstallResult]:
    results: list[InstallResult] = []

    if dep_ids and "preflight" not in dep_ids:
        if not run_preflight(config_dir, log):
            return results

    for dep_id in dep_ids:
        results.append(install_dependency(dep_id, config, log, config_dir))

    return results
