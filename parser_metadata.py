from zone import ZoneType


def parse_metadata_body(line_number: int, metadata: str) -> str:
    if not metadata:
        return ""
    if not metadata.startswith("[") or not metadata.endswith("]"):
        raise ValueError(
            f"line {line_number}: metadata must be wrapped in []"
        )
    body = metadata[1:-1]
    body = body.strip()
    if not body:
        raise ValueError(
            f"line {line_number}: metadata body is empty"
        )
    return body


def parse_metadata_pair(
    line_number: int,
    metadata_body: str
) -> tuple[str, str]:
    if "=" not in metadata_body:
        raise ValueError(
            f"line {line_number}: metadata must contain ="
        )
    parts = metadata_body.split("=", 1)
    key = parts[0]
    value = parts[1]
    key = key.strip()
    value = value.strip()
    if not key or not value:
        raise ValueError(
            f"line {line_number}: metadata key or value cannot be empty"
        )
    return key, value


def parse_metadata_pairs(
    line_number: int,
    metadata_body: str
) -> list[tuple[str, str]]:
    metadata_pairs = []

    for metadata_part in metadata_body.split():
        key, value = parse_metadata_pair(line_number, metadata_part)
        metadata_pairs.append((key, value))

    return metadata_pairs


def parse_zone_type(
    line_number: int,
    value: str
) -> ZoneType:
    if value == "normal":
        return ZoneType.NORMAL
    if value == "blocked":
        return ZoneType.BLOCKED
    if value == "restricted":
        return ZoneType.RESTRICTED
    if value == "priority":
        return ZoneType.PRIORITY
    raise ValueError(
       f"line {line_number}: unsupported zone type: {value}"
    )


def parse_hub_metadata(
    line_number: int,
    metadata: str
) -> tuple[str | None, ZoneType, int]:
    metadata_body = parse_metadata_body(line_number, metadata)
    color = None
    zone_type = ZoneType.NORMAL
    max_drones = 1

    if not metadata_body:
        return color, zone_type, max_drones

    metadata_pairs = parse_metadata_pairs(line_number, metadata_body)

    for key, value in metadata_pairs:
        if key == "color":
            color = value
        elif key == "zone":
            zone_type = parse_zone_type(line_number, value)
        elif key == "max_drones":
            try:
                max_drones = int(value)
            except ValueError:
                raise ValueError(
                    f"line {line_number}: "
                    "max_drones must be a positive integer"
                ) from None

            if max_drones < 1:
                raise ValueError(
                    f"line {line_number}: "
                    "max_drones must be greater than zero"
                )
        else:
            raise ValueError(
                f"line {line_number}: unsupported hub metadata key: {key}"
            )

    return color, zone_type, max_drones
