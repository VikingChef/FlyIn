from dataclasses import dataclass, field

from connection import Connection
from zone import Zone


@dataclass
class Map:
    zones: dict[str, Zone]
    connections: list[Connection]
    start_zone: Zone
    end_zone: Zone
    adjacency: dict[str, list[Connection]] = field(init=False)

    def __post_init__(self):
        if self.start_zone == self.end_zone:
            raise ValueError(
                "start_zone cannot be the same as end_zone"
            )

        if self.start_zone.name not in self.zones:
            raise ValueError(
                "start_zone is unknown"
            )

        if self.end_zone.name not in self.zones:
            raise ValueError(
                "end_zone is unknown"
            )

        self.adjacency = {}

        for zone_name in self.zones:
            self.adjacency[zone_name] = []

        for connection in self.connections:
            zone_a_name = connection.zone_a.name
            zone_b_name = connection.zone_b.name

            if zone_a_name not in self.zones:
                raise ValueError(
                    f"connection uses unknown zone: {zone_a_name}"
                )

            if zone_b_name not in self.zones:
                raise ValueError(
                    f"connection uses unknown zone: {zone_b_name}"
                )

            self.adjacency[zone_a_name].append(connection)
            self.adjacency[zone_b_name].append(connection)

    def get_connections(self, zone: Zone):
        if zone.name not in self.zones:
            raise ValueError(
                f"zone is not in map: {zone.name}"
            )
        return self.adjacency[zone.name]
