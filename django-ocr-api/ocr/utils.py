import pymupdf
import requests


def read_file(pdf_path: str) -> pymupdf.Document:
    if pdf_path.startswith("http"):
        r = requests.get(pdf_path)
        print(r.content)
        return pymupdf.Document(stream=r.content)

    return pymupdf.open(pdf_path)


def format_pdf_text(lines):
    # Group lines by their y-coordinate (within a threshold)
    threshold = 10
    line_groups = {}

    # Find leftmost x coordinate to use as reference point
    min_x = min(line.x_left for line in lines)

    for line in lines:
        y = line.y_top
        # Find the closest group
        group_y = None
        for existing_y in line_groups:
            if abs(existing_y - y) < threshold:
                group_y = existing_y
                break
        if group_y is None:
            group_y = y
        if group_y not in line_groups:
            line_groups[group_y] = []
        line_groups[group_y].append(line)

    # Sort groups by y-coordinate
    result = []
    for y in sorted(line_groups.keys()):
        # Sort lines within group by x-coordinate
        lines_in_group = sorted(line_groups[y], key=lambda l: l.x_left)

        # Build line with proper spacing
        current_x = min_x
        line_text = ""
        for line in lines_in_group:
            # Add spaces based on x position
            spaces_needed = int(
                (line.x_left - current_x) / 5
            )  # Divide by 5 to scale down
            line_text += " " * spaces_needed + line.text
            current_x = line.x_right

        result.append(line_text)

    return "\n".join(result)
