import logging
from pathlib import Path

import numpy as np
import pymupdf
from django.conf import settings
from paddleocr import PaddleOCR
from PIL import Image

from .utils import Document, Page, read_file

ppocr_logger = logging.getLogger("ppocr")
ppocr_logger.setLevel(logging.INFO)

logger = logging.getLogger(settings.APP_NAME)


class OcrEngine:
    def __init__(self):
        logger.info("Initializing OCR engine")
        self.model = PaddleOCR(
            cls_model_dir=(settings.PADDLE_MODELS_DIR / "ch_ppocr_mobile_v2.0_cls_infer.onnx").as_posix(),
            det_model_dir=(settings.PADDLE_MODELS_DIR / "Multilingual_PP-OCRv3_det_infer.onnx").as_posix(),
            rec_model_dir=(settings.PADDLE_MODELS_DIR / "latin_PP-OCRv3_rec_infer.onnx").as_posix(),
            use_angle_cls=False,
            use_gpu=False,
            use_onnx=True,
            lang="fr",
        )

    def ocr_document(self, file_path: str) -> Document:
        logger.info(f"OCR document at {file_path=}")
        document = read_file(file_path)
        pages = []
        for page in document:
            result = self.ocr_page(page)
            pages.append(Page(page.number, result[0]))
        return Document(file_path, pages)

    def ocr_document_multi(self, file_path: str) -> Document:
        logger.info(f"OCR multiple files in single document at {file_path=}")
        page_no = 0
        pages = []
        for f in Path(file_path).glob("*"):
            document = read_file(f.as_posix())
            for page in document:
                result = self.ocr_page(page)
                pages.append(Page(page_no, result[0]))
                page_no += 1
        return Document(file_path, pages)

    def ocr_page(self, page: pymupdf.Page) -> list:
        mat = pymupdf.Matrix(2, 2)
        pm = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.frombytes("RGB", [pm.width, pm.height], pm.samples)

        return self.model.ocr(np.array(img), cls=False)[0], img
