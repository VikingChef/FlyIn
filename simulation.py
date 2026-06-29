from dataclasses import dataclass, field

from drone import Drone
from map import Map


@dataclass
class Simulation:
    nb_drones: int
    map: Map
    drones: list[Drone] = field(init=False)
    turn: int = field(default=0, init=False)

    def __post_init__(self):
        if self.nb_drones <= 0:
            raise ValueError(
                "nb_drones must be greater than 0"
            )

        self.drones = []

        for drone_id in range(1, self.nb_drones + 1):
            drone = Drone(
                drone_id,
                self.map.start_zone,
                self.map.end_zone
            )
            self.drones.append(drone)

    def all_drones_arrived(self) -> bool:
        for drone in self.drones:
            if not drone.has_arrived():
                return False
        return True
