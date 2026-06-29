from dataclasses import dataclass

from drone import Drone
from zone import Zone
from connection import Connection


@dataclass
class ProposedMove:
    drone: Drone
    from_zone: Zone
    to_zone: Zone
    connection: Connection
