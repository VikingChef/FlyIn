from dataclasses import dataclass

from zone import Zone


@dataclass
class Drone:
    id: int
    current_zone: Zone
    destination: Zone

    def has_arrived(self) -> bool:
        return self.current_zone == self.destination
