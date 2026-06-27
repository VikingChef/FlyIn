from zone import Zone
from connection import Connection
from map import Map
from parser_lines import (
    read_clean_lines,
    is_hub_line,
    is_drone_count_line,
    is_connection_line
)
from parser_hubs import (
    parse_drone_count,
    parse_hubs,
    parse_zone_from_hub_line,
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
    zone_a_name, zone_b_name = parse_connection_names(line_number, body)
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
    return Connection(zone_a, zone_b)


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


def validate_known_lines(
    cleaned_lines: list[tuple[int, str]]
) -> None:
    for line_number, line in cleaned_lines:
        if (
            is_drone_count_line(line)
            or is_hub_line(line)
            or is_connection_line(line)
        ):
            continue

        raise ValueError(
            f"line {line_number}: unknown line type"
        )


def validate_connection_order(
    cleaned_lines: list[tuple[int, str]]
) -> None:
    seen_zone_names: set[str] = set()

    for line_number, line in cleaned_lines:
        if is_hub_line(line):
            _, zone = parse_zone_from_hub_line(line_number, line)
            seen_zone_names.add(zone.name)
            continue

        if is_connection_line(line):
            body = parse_connection_body(line_number, line)
            zone_a_name, zone_b_name = parse_connection_names(
                line_number,
                body
            )
            if zone_a_name not in seen_zone_names:
                raise ValueError(
                    f"line {line_number}: "
                    "connection uses zone before definition"
                )

            if zone_b_name not in seen_zone_names:
                raise ValueError(
                    f"line {line_number}: "
                    "connection uses zone before definition"
                )


def validate_drone_count_position(
    cleaned_lines: list[tuple[int, str]]
) -> None:
    for line_number, line in cleaned_lines[1:]:
        if is_drone_count_line(line):
            raise ValueError(
                f"line {line_number}: duplicate nb_drones definition"
            )


def parse_map_file(
    file_path: str
) -> tuple[int, Map]:
    cleaned_lines = read_clean_lines(file_path)
    validate_known_lines(cleaned_lines)
    validate_connection_order(cleaned_lines)
    validate_drone_count_position(cleaned_lines)
    nb_drones = parse_drone_count(cleaned_lines)
    zones, start_zone, end_zone = parse_hubs(cleaned_lines)
    connections = parse_connections(cleaned_lines, zones)
    parsed_map = Map(zones, connections, start_zone, end_zone)
    return nb_drones, parsed_map
