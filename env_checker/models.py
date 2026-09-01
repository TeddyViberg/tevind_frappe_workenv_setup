from dataclasses import dataclass
from enum import Enum


class Status(Enum):
    OK = "ok"
    MISSING = "missing"
    OUTDATED = "outdated"
    WARN = "warn"

    @property
    def label(self) -> str:
        return {
            Status.OK: "OK",
            Status.MISSING: "Missing",
            Status.OUTDATED: "Outdated",
            Status.WARN: "Warning",
        }[self]

    @property
    def is_good(self) -> bool:
        return self == Status.OK


@dataclass
class CheckResult:
    id: str
    name: str
    required: str
    installed: str
    status: Status
    hint: str = ""
    updatable: bool = True

    @property
    def passed(self) -> bool:
        return self.status.is_good

    @property
    def needs_update(self) -> bool:
        return not self.passed and self.updatable
