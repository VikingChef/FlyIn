from dataclasses import dataclass, field

from drone import Drone
from map import Map
from connection import Connection
from move import ProposedMove
from zone import ZoneType


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

    def create_proposed_move(
        self,
        drone: Drone,
        connection: Connection
    ) -> ProposedMove:
        from_zone = drone.current_zone
        to_zone = connection.get_other_zone(from_zone)

        return ProposedMove(
            drone,
            from_zone,
            to_zone,
            connection
        )

    def is_blocked_move(self, move: ProposedMove) -> bool:
        if move.to_zone.zone_type == ZoneType.BLOCKED:
            return True
        return False

    def count_connection_moves(
        self,
        moves: list[ProposedMove],
        connection: Connection,
    ) -> int:
        count = 0

        for move in moves:
            if move.connection == connection:
                count += 1

        return count

    def apply_move(self, move: ProposedMove) -> None:
        move.drone.current_zone = move.to_zone

    def apply_moves(self, moves: list[ProposedMove]) -> None:
        for move in moves:
            self.apply_move(move)

    def complete_turn(self, accepted_moves: list[ProposedMove]) -> None:
        self.apply_moves(accepted_moves)
        self.turn += 1

    def has_movement(self, accepted_moves: list[ProposedMove]) -> bool:
        if accepted_moves:
            return True
        return False

    def all_drones_arrived(self) -> bool:
        for drone in self.drones:
            if not drone.has_arrived():
                return False
        return True

    def has_failed_turn(self, accepted_moves: list[ProposedMove]) -> bool:
        if (
            not self.has_movement(accepted_moves)
            and not self.all_drones_arrived()
        ):
            return True
        return False
