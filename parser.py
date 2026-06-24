def clean_line(line: str) -> str:
    cleaned = line.split("#")[0]
    cleaned = cleaned.strip()
    return cleaned


def read_clean_lines(file_path: str) -> list[tuple[int, str]]:
    cleaned_lines = []

    with open(file_path) as file:
        for line_number, raw_line in enumerate(file, start=1):
            cleaned = clean_line(raw_line)

            if cleaned:
                cleaned_lines.append((line_number, cleaned))

    return cleaned_lines


def parse_nb_drones(line_number: int, line: str) -> int:
    if not line.startswith("nb_drones:"):
        raise ValueError(
            f"line {line_number}: expected nb_drones definition"
        )
    value_text = line.split(":", 1)[1]
    value_text = value_text.strip()
    try:
        nb_drones = int(value_text)
    except ValueError:
        raise ValueError(
            f"line {line_number}: nb_drones must be a positive integer"
        ) from None
    if nb_drones <= 0:
        raise ValueError(
            f"line {line_number}: nb_drones must be a positive integer"
        )
    return nb_drones
