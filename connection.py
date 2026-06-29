from dataclasses import dataclass

from zone import Zone


@dataclass(frozen=True)
class Connection:
    zone_a: Zone
    zone_b: Zone
    max_link_capacity: int = 1

    def __post_init__(self):
        if self.max_link_capacity <= 0:
            raise ValueError(
                "max_link_capacity must be greater than 0"
            )
        if self.zone_a == self.zone_b:
            raise ValueError(
                "connection zones must be different"
            )

    def get_other_zone(self, zone: Zone) -> Zone:
        if zone == self.zone_a:
            return self.zone_b

        if zone == self.zone_b:
            return self.zone_a

        raise ValueError(
            "zone is not part of connection"
        )
