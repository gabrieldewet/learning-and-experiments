import logging

import numpy as np
import pymupdf
from attrs import define, field
from django.conf import settings
from paddleocr import PaddleOCR
from PIL import Image

from .utils import format_pdf_text, read_file

ppocr_logger = logging.getLogger("ppocr")
ppocr_logger.setLevel(logging.INFO)

logger = logging.getLogger(settings.APP_NAME)


class OcrEngine:
    def __init__(self):
        logger.info("Initializing OCR engine")
        self.model = PaddleOCR(
            cls_model_dir=settings.PADDLE_MODELS_DIR
            / "ch_ppocr_mobile_v2.0_cls_infer.onnx",
            det_model_dir=settings.PADDLE_MODELS_DIR
            / "Multilingual_PP-OCRv3_det_infer.onnx",
            rec_model_dir=settings.PADDLE_MODELS_DIR / "latin_PP-OCRv3_rec_infer.onnx",
            use_angle_cls=False,
            use_gpu=False,
            use_onnx=True,
            lang="fr",
        )

    def ocr_document(self, file_path: str):
        document = read_file(file_path)
        pages = []
        for page in document:
            result = self.ocr_page(page)
            pages.append(Page(page.number, result[0]))
        return Document(file_path, pages)

    def ocr_page(self, page: pymupdf.Page):
        mat = pymupdf.Matrix(2, 2)
        pm = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.frombytes("RGB", [pm.width, pm.height], pm.samples)
        return self.model.ocr(np.array(img), cls=False), img


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
    lines: list[Line] = field(
        converter=lambda x: [Line(box[1][0], box[0]) for box in x]
    )
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
