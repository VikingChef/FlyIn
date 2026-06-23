def clean_line(line: str) -> str:
    cleaned = line.split("#")[0]
    cleaned = cleaned.strip()
    return cleaned
