import re


def parse_version(version: str) -> tuple[int, ...]:
    version = version.strip().lstrip("v")
    parts: list[int] = []
    for segment in re.split(r"[.\-]", version):
        if segment.isdigit():
            parts.append(int(segment))
        else:
            break
    return tuple(parts)


def version_ge(installed: str, minimum: str) -> bool:
    a, b = parse_version(installed), parse_version(minimum)
    length = max(len(a), len(b))
    a_padded = a + (0,) * (length - len(a))
    b_padded = b + (0,) * (length - len(b))
    return a_padded >= b_padded
