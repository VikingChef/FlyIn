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


def is_drone_count_line(line: str) -> bool:
    if line.startswith("nb_drones:"):
        return True
    return False


def is_hub_line(line: str) -> bool:
    if line.startswith("start_hub:"):
        return True
    if line.startswith("end_hub:"):
        return True
    if line.startswith("hub:"):
        return True
    return False


def is_connection_line(line: str) -> bool:
    if line.startswith("connection:"):
        return True
    return False
