import pymupdf
import requests
from attrs import define, field
from django.core.files.uploadedfile import UploadedFile


@define
class Line:
    text: str
    input_bbox: list[list[float]] = field(repr=False)
    y_top: int = field(init=False, repr=False)
    y_bottom: int = field(init=False, repr=False)
    x_left: int = field(init=False, repr=False)
    x_right: int = field(init=False, repr=False)

    output_bbox: list[tuple[int]] = field(init=False)

    def __attrs_post_init__(self):
        top_left, top_right, bottom_right, bottom_left = self.input_bbox

        self.y_top = int(min(top_left[1], top_right[1]))
        self.y_bottom = int(max(bottom_left[1], bottom_right[1]))
        self.x_left = int(min(top_left[0], bottom_left[0]))
        self.x_right = int(max(top_right[0], bottom_right[0]))

        self.set_ouptut_bbox()

    def set_ouptut_bbox(self):
        top_left = (self.x_left, self.y_top)
        top_right = (self.x_right, self.y_top)
        bottom_right = (self.x_right, self.y_bottom)
        bottom_left = (self.x_left, self.y_bottom)

        self.output_bbox = [top_left, top_right, bottom_right, bottom_left]

    def same_level(self, other: "Line", y_threshold: int = 20):
        # Check if midpoints align
        self_mid = (self.y_top + self.y_bottom) / 2
        other_mid = (other.y_top + other.y_bottom) / 2
        close_mid = abs(self_mid - other_mid) < y_threshold

        # Check if box height align
        self_height = self.y_bottom - self.y_top
        other_height = other.y_bottom - other.y_top
        close_height = abs(self_height - other_height) < y_threshold

        return close_mid and close_height


@define
class Page:
    page_number: int
    lines: list[Line] = field(converter=lambda x: [Line(box[1][0], box[0]) for box in x])
    sorted_lines: list[Line] = field(init=False)
    text: str = field(init=False)

    def __attrs_post_init__(self):
        # Realign lines
        self.sorted_lines = self.realign_lines(self.lines)
        self.text = format_pdf_text(self.sorted_lines)

    @staticmethod
    def realign_lines(lines: list[Line]):
        for i in range(len(lines)):
            for j in range(0, len(lines) - i - 1):
                current_line = lines[j]
                next_line = lines[j + 1]

                if current_line.same_level(next_line):
                    lines[j + 1].y_top = current_line.y_top
                    lines[j + 1].y_bottom = current_line.y_bottom

                lines[i + 1].set_ouptut_bbox()
        return sorted(lines, key=lambda x: (x.y_top, x.x_left))


@define
class Document:
    file_path: str
    pages: list[Page]

    @property
    def formatted_results(self):
        return {
            "file_path": self.file_path,
            "pages": [
                {
                    "page_number": page.page_number,
                    "lines": [{"text": line.text, "bbox": line.output_bbox} for line in page.sorted_lines],
                    "text": page.text,
                }
                for page in self.pages
            ],
        }


def read_file(pdf_path: str) -> pymupdf.Document:
    if pdf_path.startswith("http"):
        r = requests.get(pdf_path)
        print(r.content)
        return pymupdf.Document(stream=r.content)

    return pymupdf.open(pdf_path)


def format_pdf_text(lines: list[Line]) -> str:
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
        lines_in_group = sorted(line_groups[y], key=lambda x: x.x_left)

        # Build line with proper spacing
        current_x = min_x
        line_text = ""
        for line in lines_in_group:
            # Add spaces based on x position
            spaces_needed = int((line.x_left - current_x) / 5)  # Divide by 5 to scale down
            line_text += " " * spaces_needed + line.text
            current_x = line.x_right

        result.append(line_text)

    return "\n".join(result)
