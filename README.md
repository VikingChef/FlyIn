# Fly-in

## Project Philosophy

* Design first, code second.
* Avoid over-engineering.
* Avoid duplicate implementations.
* Move responsibilities when necessary rather than rewriting them.
* Prefer explicit errors over generic error messages.
* Store information in the object that owns it.
* Do not store information that can be derived from existing state.

## Architecture Decisions

### Zone

A Zone represents a place in the world.

Zone owns:

* name
* x
* y
* zone_type
* color
* max_drones

Zone does not own connections.
Zone validates that max_drones is greater than 0.

### Connection

A Connection represents a bidirectional route between two zones.

Connection stores references to Zone objects, not zone names.
The parser resolves zone names before creating Connection objects.
Connection is immutable after parsing.
Connection validates that max_link_capacity is greater than 0.
Connection validates that both zones are different.

### Map

Map represents the world and the relationships between zones.

Map owns:

* zones
* connections
* adjacency structure
* start_zone
* end_zone

Start and end hubs are represented as normal Zone objects.
Map stores which Zone is the start and end of the world.

Map does not own:

* drones
* simulation state
* nb_drones

### Drone

A Drone represents drone state.

Drone owns:

* id
* current_zone
* destination

Drone does not own:

* path
* visited zones
* routing decisions

### Simulation

Simulation manages drones moving through the world.

Simulation owns:

* drones
* turn counter
* pending moves
* movement logic
* conflict resolution

## Parsing Decisions

* Parser creates project objects.
* Zones are parsed before connections.
* Map is created after parsing and validation.
* Parser hands a finished world to Map.
* Comments are ignored.
* Blank lines are ignored.

## Validation Decisions

Invalid:

* Unknown zones in connections
* Duplicate connections
* Self-connections
* Start and end referring to the same zone
* Paths that use blocked zones

## Pathfinding Decisions

Primary objective:

* Fewest turns

Tie breaker:

* Prefer priority zones

Zone costs:

* normal = 1 turn
* priority = 1 turn
* restricted = 2 turns
* blocked = invalid

## Simulation Decisions

All drones exist at simulation startup.

All drones begin at the start zone.

Turn flow:

1. Gather proposed moves
2. Resolve conflicts
3. Apply accepted moves
4. Increment turn counter

A drone may:

* Move
* Wait

Waiting is considered a valid action.

## Termination Conditions

Success:

* All drones reach the destination

Guard failure:

* A full turn completes with no drone movement before all drones arrive

## Notes

* Color values are treated as arbitrary strings.
* Project decisions that are not explicitly defined in the PDF should be documented here.
