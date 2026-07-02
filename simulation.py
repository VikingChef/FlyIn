from dataclasses import dataclass, field

from drone import Drone
from map import Map
from connection import Connection
from move import ProposedMove
from zone import ZoneType, Zone


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

    def get_drone_candidate_moves(
        self,
        drone: Drone,
    ) -> list[ProposedMove]:
        candidate_moves = []

        for connection in self.map.get_connections(drone.current_zone):
            candidate_moves.append(
                self.create_proposed_move(drone, connection)
            )

        return candidate_moves

    def choose_drone_move(
        self,
        drone: Drone,
    ) -> ProposedMove | None:
        candidate_moves = self.get_non_blocked_candidate_moves(drone)

        for move in candidate_moves:
            if move.to_zone == drone.destination:
                return move

        return None

    def get_proposed_moves(self) -> list[ProposedMove]:
        proposed_moves = []

        for drone in self.drones:
            move = self.choose_drone_move(drone)

            if move is not None:
                proposed_moves.append(move)

        return proposed_moves

    def is_blocked_move(self, move: ProposedMove) -> bool:
        if move.to_zone.zone_type == ZoneType.BLOCKED:
            return True
        return False

    def get_non_blocked_candidate_moves(
        self,
        drone: Drone,
    ) -> list[ProposedMove]:
        allowed_moves = []

        for move in self.get_drone_candidate_moves(drone):
            if not self.is_blocked_move(move):
                allowed_moves.append(move)

        return allowed_moves

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

    def is_connection_over_capacity(
        self,
        moves: list[ProposedMove],
        connection: Connection,
    ) -> bool:
        if (
            self.count_connection_moves(moves, connection)
            > connection.max_link_capacity
        ):
            return True
        return False

    def get_remaining_connection_capacity(
        self,
        accepted_moves: list[ProposedMove],
        connection: Connection,
    ) -> int:
        return connection.max_link_capacity - self.count_connection_moves(
            accepted_moves,
            connection,
        )

    def count_zone_arrivals(
        self,
        moves: list[ProposedMove],
        zone: Zone,
    ) -> int:
        count = 0

        for move in moves:
            if move.to_zone == zone:
                count += 1

        return count

    def is_zone_over_capacity(
        self,
        moves: list[ProposedMove],
        zone: Zone,
    ) -> bool:
        if self.count_zone_arrivals(moves, zone) > zone.max_drones:
            return True
        return False

    def get_remaining_zone_capacity(
        self,
        accepted_moves: list[ProposedMove],
        zone: Zone,
    ) -> int:
        return zone.max_drones - self.count_zone_arrivals(
            accepted_moves,
            zone,
        )

    def can_accept_contested_move(
        self,
        accepted_moves: list[ProposedMove],
        move: ProposedMove,
    ) -> bool:
        if self.get_remaining_connection_capacity(
            accepted_moves,
            move.connection,
        ) <= 0:
            return False

        if self.get_remaining_zone_capacity(
            accepted_moves,
            move.to_zone,
        ) <= 0:
            return False

        return True

    def accept_contested_moves(
        self,
        accepted_moves: list[ProposedMove],
        contested_moves: list[ProposedMove],
    ) -> list[ProposedMove]:
        resolved_moves = list(accepted_moves)

        for move in contested_moves:
            if self.can_accept_contested_move(resolved_moves, move):
                resolved_moves.append(move)

        return resolved_moves

    def resolve_accepted_moves(
        self,
        moves: list[ProposedMove],
    ) -> list[ProposedMove]:
        accepted_moves = self.get_initial_accepted_moves(moves)
        contested_moves = self.get_contested_moves(moves)

        return self.accept_contested_moves(
            accepted_moves,
            contested_moves,
        )

    def resolve_turn(
        self,
        moves: list[ProposedMove],
    ) -> list[ProposedMove]:
        accepted_moves = self.resolve_accepted_moves(moves)

        self.complete_turn(accepted_moves)

        return accepted_moves

    def run_turn(self) -> list[ProposedMove]:
        proposed_moves = self.get_proposed_moves()

        return self.resolve_turn(proposed_moves)

    def is_over_capacity_move(
        self,
        moves: list[ProposedMove],
        move: ProposedMove,
    ) -> bool:
        if self.is_connection_over_capacity(moves, move.connection):
            return True

        if self.is_zone_over_capacity(moves, move.to_zone):
            return True

        return False

    def is_rule_rejected_move(
        self,
        move: ProposedMove,
    ) -> bool:
        if self.is_blocked_move(move):
            return True

        return False

    def is_contested_move(
        self,
        moves: list[ProposedMove],
        move: ProposedMove,
    ) -> bool:
        if self.is_over_capacity_move(moves, move):
            return True

        return False

    def get_uncontested_moves(
        self,
        moves: list[ProposedMove],
    ) -> list[ProposedMove]:
        uncontested_moves = []

        for move in moves:
            if (
                not self.is_rule_rejected_move(move)
                and not self.is_contested_move(moves, move)
            ):
                uncontested_moves.append(move)

        return uncontested_moves

    def get_contested_moves(
        self,
        moves: list[ProposedMove],
    ) -> list[ProposedMove]:
        contested_moves = []

        for move in moves:
            if (
                not self.is_rule_rejected_move(move)
                and self.is_contested_move(moves, move)
            ):
                contested_moves.append(move)

        return contested_moves

    def get_rule_rejected_moves(
        self,
        moves: list[ProposedMove],
    ) -> list[ProposedMove]:
        rejected_moves = []

        for move in moves:
            if self.is_rule_rejected_move(move):
                rejected_moves.append(move)

        return rejected_moves

    def get_initial_accepted_moves(
        self,
        moves: list[ProposedMove],
    ) -> list[ProposedMove]:
        return self.get_uncontested_moves(moves)

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
