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
from parser_connections import (
    parse_connection_body,
    parse_connection_names,
    parse_connections
)


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
