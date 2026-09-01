import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Optional

from env_checker.models import CheckResult, Status
from env_checker.version import version_ge

NVM_SCRIPT = Path.home() / ".nvm" / "nvm.sh"


def load_config(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def run_command(command: list[str], shell: bool = False) -> Optional[str]:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=15,
            shell=shell,
        )
        output = (result.stdout or result.stderr or "").strip()
        return output if output else None
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None


def extract_version(output: str, pattern: str) -> Optional[str]:
    match = re.search(pattern, output)
    return match.group(1) if match else None


def _result(
    dep: dict[str, Any],
    installed: str,
    status: Status,
    hint: str = "",
) -> CheckResult:
    return CheckResult(
        id=dep.get("id", ""),
        name=dep["name"],
        required=dep["required"],
        installed=installed,
        status=status,
        hint=hint or dep.get("install_hint", ""),
        updatable=dep.get("updatable", True),
    )


def check_os(dep: dict[str, Any], os_req: dict[str, Any]) -> CheckResult:
    release = run_command(["lsb_release", "-rs"])
    distro_id = run_command(["lsb_release", "-is"])
    message = os_req.get("message", "Ubuntu 24.04+ or Debian 13+")

    if not release or not distro_id:
        return _result(
            dep,
            "unknown",
            Status.WARN,
            "Could not detect OS via lsb_release",
        )

    release = release.strip()
    distro = distro_id.strip().lower()
    label = f"{distro_id.strip()} {release}"

    if distro == "ubuntu":
        ok = version_ge(release, os_req.get("ubuntu_min", "24.04"))
    elif distro == "debian":
        ok = version_ge(release, os_req.get("debian_min", "13"))
    else:
        return _result(
            dep,
            label,
            Status.WARN,
            f"Untested distro: {distro_id.strip()}",
        )

    return _result(
        dep,
        label,
        Status.OK if ok else Status.OUTDATED,
        "" if ok else "Upgrade to Ubuntu 24.04+ or Debian 13+",
    )


def check_nvm(dep: dict[str, Any]) -> CheckResult:
    if not NVM_SCRIPT.is_file():
        return _result(dep, "not found", Status.MISSING)

    output = run_command(f"source '{NVM_SCRIPT}' && nvm --version", shell=True)
    if not output:
        return _result(dep, "not found", Status.MISSING)

    return _result(dep, output.strip(), Status.OK)


def check_pip(dep: dict[str, Any]) -> CheckResult:
    output = run_command(["python3", "-m", "pip", "--version"])
    if not output:
        return _result(dep, "not found", Status.MISSING)

    version = extract_version(output, r"pip ([\d.]+)")
    if not version:
        return _result(dep, output, Status.WARN)

    min_ver = dep.get("min_version")
    if min_ver and not version_ge(version, min_ver):
        return _result(dep, version, Status.OUTDATED)

    return _result(dep, version, Status.OK)


def check_command(dep: dict[str, Any]) -> CheckResult:
    command = dep["command"]

    if shutil.which(command[0]) is None:
        return _result(dep, "not found", Status.MISSING)

    output = run_command(command)
    if not output:
        return _result(dep, "error", Status.MISSING)

    pattern = dep.get("pattern")
    if not pattern:
        return _result(dep, "installed", Status.OK)

    version = extract_version(output, pattern)
    if not version:
        return _result(dep, output.split("\n")[0], Status.WARN)

    min_ver = dep.get("min_version")
    if min_ver:
        if version_ge(version, min_ver):
            return _result(dep, version, Status.OK)
        return _result(dep, version, Status.OUTDATED)

    return _result(dep, version, Status.OK)


def run_checks(config: dict[str, Any]) -> list[CheckResult]:
    results: list[CheckResult] = []
    os_req = config.get("os_requirements", {})

    dispatch = {
        "os": lambda dep: check_os(dep, os_req),
        "nvm": check_nvm,
        "pip": check_pip,
        "command": check_command,
    }

    for dep in config.get("dependencies", []):
        check_type = dep.get("check", "command")
        checker = dispatch.get(check_type, check_command)
        results.append(checker(dep))

    return results
