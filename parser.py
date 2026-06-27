from map import Map
from parser_lines import (
    read_clean_lines,
)
from parser_hubs import (
    parse_drone_count,
    parse_hubs,
)
from parser_validation import (
    validate_known_lines,
    validate_connection_order,
    validate_drone_count_position,
)
from parser_connections import parse_connections


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
