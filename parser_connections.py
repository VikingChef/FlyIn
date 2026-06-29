from zone import Zone
from connection import Connection
from parser_lines import is_connection_line
from parser_metadata import (
    parse_metadata_body,
    parse_metadata_pair,
)


def parse_connection_body(
    line_number: int,
    line: str
) -> str:
    if not line.startswith("connection:"):
        raise ValueError(
            f"line {line_number}: expected connection definition"
        )

    parts = line.split(":", 1)
    body = parts[1]
    body = body.strip()

    if not body:
        raise ValueError(
            f"line {line_number}: connection line is missing body"
        )

    return body


def parse_connection_fields(
    line_number: int,
    body: str
) -> tuple[str, str]:
    parts = body.split(maxsplit=1)

    connection_text = parts[0]

    if len(parts) == 2:
        metadata = parts[1]
    else:
        metadata = ""

    return connection_text, metadata


def parse_connection_capacity(
    line_number: int,
    metadata: str
) -> int:
    metadata_body = parse_metadata_body(line_number, metadata)

    if not metadata_body:
        return 1

    key, value = parse_metadata_pair(line_number, metadata_body)

    if key != "max_link_capacity":
        raise ValueError(
            f"line {line_number}: unsupported connection metadata key {key}"
        )

    try:
        max_link_capacity = int(value)
    except ValueError:
        raise ValueError(
            f"line {line_number}: must be a positive integer"
        ) from None

    if max_link_capacity < 1:
        raise ValueError(
            f"line {line_number}: capacity must be greater than zero"
        )

    return max_link_capacity


def parse_connection_names(
    line_number: int,
    body: str
) -> tuple[str, str]:
    parts = body.split("-")

    if len(parts) != 2:
        raise ValueError(
            f"line {line_number}: connection must use exactly one dash"
        )

    zone_a_name = parts[0].strip()
    zone_b_name = parts[1].strip()

    if not zone_a_name or not zone_b_name:
        raise ValueError(
            f"line {line_number}: connection zone names cannot be empty"
        )

    return zone_a_name, zone_b_name


def parse_connection_from_line(
    line_number: int,
    line: str,
    zones: dict[str, Zone]
) -> Connection:
    body = parse_connection_body(line_number, line)
    connection_text, metadata = parse_connection_fields(line_number, body)
    capacity = parse_connection_capacity(line_number, metadata)
    zone_a_name, zone_b_name = parse_connection_names(
        line_number,
        connection_text
    )
    if zone_a_name not in zones:
        raise ValueError(
            f"line {line_number}: unknown zone in connection: {zone_a_name}"
        )
    if zone_b_name not in zones:
        raise ValueError(
            f"line {line_number}: unknown zone in connection: {zone_b_name}"
        )
    if zone_a_name == zone_b_name:
        raise ValueError(
            f"line {line_number}: connection zones must be different"
        )
    zone_a = zones[zone_a_name]
    zone_b = zones[zone_b_name]
    return Connection(
        zone_a,
        zone_b,
        max_link_capacity=capacity,
    )


def parse_connections(
    cleaned_lines: list[tuple[int, str]],
    zones: dict[str, Zone]
) -> list[Connection]:
    connections: list[Connection] = []
    seen_connections: set[tuple[str, str]] = set()

    for line_number, line in cleaned_lines:
        if is_connection_line(line):
            connection = parse_connection_from_line(line_number, line, zones)

            zone_a_name = connection.zone_a.name
            zone_b_name = connection.zone_b.name
            if zone_a_name < zone_b_name:
                first_name = zone_a_name
                second_name = zone_b_name
            else:
                first_name = zone_b_name
                second_name = zone_a_name

            connection_key = (first_name, second_name)

            if connection_key in seen_connections:
                raise ValueError(
                    f"line {line_number}: duplicate connection"
                )

            seen_connections.add(connection_key)
            connections.append(connection)

    return connections
