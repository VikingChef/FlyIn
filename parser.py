from zone import Zone


def clean_line(line: str) -> str:
    cleaned = line.split("#")[0]
    cleaned = cleaned.strip()
    return cleaned


def read_clean_lines(file_path: str) -> list[tuple[int, str]]:
    cleaned_lines = []

    with open(file_path) as file:
        for line_number, raw_line in enumerate(file, start=1):
            cleaned = clean_line(raw_line)

            if cleaned:
                cleaned_lines.append((line_number, cleaned))

    return cleaned_lines


def parse_nb_drones(line_number: int, line: str) -> int:
    if not line.startswith("nb_drones:"):
        raise ValueError(
            f"line {line_number}: expected nb_drones definition"
        )
    value_text = line.split(":", 1)[1]
    value_text = value_text.strip()
    try:
        nb_drones = int(value_text)
    except ValueError:
        raise ValueError(
            f"line {line_number}: nb_drones must be a positive integer"
        ) from None
    if nb_drones <= 0:
        raise ValueError(
            f"line {line_number}: nb_drones must be a positive integer"
        )
    return nb_drones


def parse_drone_count(cleaned_lines: list[tuple[int, str]]) -> int:
    if not cleaned_lines:
        raise ValueError(
            "map file is empty"
        )
    line_number, line = cleaned_lines[0]
    return parse_nb_drones(line_number, line)


def parse_hub_kind(line_number: int, line: str) -> str:
    if line.startswith("start_hub:"):
        return "start"
    if line.startswith("end_hub:"):
        return "end"
    if line.startswith("hub:"):
        return "normal"
    raise ValueError(
        f"line {line_number}: invalid hub line"
    )


def parse_hub_body(line_number: int, line: str) -> str:
    parts = line.split(":", 1)
    body = parts[1]
    body = body.strip()
    if not body:
        raise ValueError(
            f"line {line_number}: hub line is missing body"
        )
    return body


def parse_hub_fields(line_number: int, body: str) -> tuple[str, str, str, str]:
    parts = body.split(maxsplit=3)
    if len(parts) < 3:
        raise ValueError(
            f"line {line_number}: hub line must contain name, x and y"
        )
    name = parts[0]
    x_text = parts[1]
    y_text = parts[2]
    if len(parts) == 4:
        metadata = parts[3]
    else:
        metadata = ""
    return name, x_text, y_text, metadata


def parse_hub_coordinates(
    line_number: int,
    x_text: str,
    y_text: str
) -> tuple[int, int]:
    try:
        x = int(x_text)
        y = int(y_text)
    except ValueError:
        raise ValueError(
            f"line {line_number}: hub x and y coordinates must be integers"
        ) from None
    return x, y


def parse_hub_line(
    line_number: int,
    line: str
) -> tuple[str, str, int, int, str]:
    kind = parse_hub_kind(line_number, line)
    body = parse_hub_body(line_number, line)
    name, x_text, y_text, metadata = parse_hub_fields(line_number, body)
    x, y = parse_hub_coordinates(line_number, x_text, y_text)
    return kind, name, x, y, metadata


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


def parse_hub_color(line_number: int, metadata: str) -> str | None:
    metadata_body = parse_metadata_body(line_number, metadata)
    if not metadata_body:
        return None
    key, value = parse_metadata_pair(line_number, metadata_body)
    if key != "color":
        raise ValueError(
            f"line {line_number}: unsupported hub metadata key: {key}"
        )
    return value


def parse_zone_from_hub_line(
    line_number: int,
    line: str
) -> tuple[str, Zone]:
    kind, name, x, y, metadata = parse_hub_line(line_number, line)
    color = parse_hub_color(line_number, metadata)
    zone = Zone(name, x, y, color=color)
    return kind, zone


def is_hub_line(line: str) -> bool:
    if line.startswith("start_hub:"):
        return True
    if line.startswith("end_hub:"):
        return True
    if line.startswith("hub:"):
        return True
    return False


def parse_hubs(
    cleaned_lines: list[tuple[int, str]]
) -> tuple[dict[str, Zone], Zone, Zone]:
    zones: dict[str, Zone] = {}
    start_zone: Zone | None = None
    end_zone: Zone | None = None
    for line_number, line in cleaned_lines:
        if is_hub_line(line):
            kind, zone = parse_zone_from_hub_line(line_number, line)
            if zone.name in zones:
                raise ValueError(
                    f"line {line_number}: duplicate zone name: {zone.name}"
                )
            zones[zone.name] = zone
            if kind == "start":
                if start_zone is not None:
                    raise ValueError(
                        f"line {line_number}: multiple start hubs"
                    )
                start_zone = zone

            if kind == "end":
                if end_zone is not None:
                    raise ValueError(
                        f"line {line_number}: multiple end hubs"
                    )
                end_zone = zone
    if start_zone is None:
        raise ValueError(
            "map is missing start_hub"
        )

    if end_zone is None:
        raise ValueError(
            "map is missing end_hub"
        )

    return zones, start_zone, end_zone
