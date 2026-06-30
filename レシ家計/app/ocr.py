from __future__ import annotations

import base64
import mimetypes
from abc import ABC, abstractmethod

from app.config import Settings
from app.models import OCRResult


class OCRProvider(ABC):
    @abstractmethod
    def extract_text(self, image_bytes: bytes, filename: str | None = None) -> OCRResult:
        raise NotImplementedError


class MockOCRProvider(OCRProvider):
    """Development provider.

    If the uploaded file is actually UTF-8 text, it is treated as OCR output.
    For real images it returns empty text, so the API can still be exercised
    without saving incorrect confirmed data.
    """

    def extract_text(self, image_bytes: bytes, filename: str | None = None) -> OCRResult:
        try:
            text = image_bytes.decode("utf-8").strip()
        except UnicodeDecodeError:
            return OCRResult(text="", confidence=0.0)

        if not text:
            return OCRResult(text="", confidence=0.0)
        return OCRResult(text=text, confidence=0.7)


class OpenAIVisionOCRProvider(OCRProvider):
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def extract_text(self, image_bytes: bytes, filename: str | None = None) -> OCRResult:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install the openai package or use RECEIPT_OCR_PROVIDER=mock.") from exc

        mime_type = mimetypes.guess_type(filename or "")[0] or "image/jpeg"
        encoded = base64.b64encode(image_bytes).decode("ascii")
        image_url = f"data:{mime_type};base64,{encoded}"

        client = OpenAI(api_key=self.api_key)
        response = client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Read this Japanese receipt image and return only the visible text. "
                                "Keep line breaks close to the original receipt. Do not summarize."
                            ),
                        },
                        {"type": "input_image", "image_url": image_url},
                    ],
                }
            ],
        )
        return OCRResult(text=response.output_text.strip(), confidence=0.85)


def build_ocr_provider(settings: Settings) -> OCRProvider:
    if settings.ocr_provider == "mock":
        return MockOCRProvider()
    if settings.ocr_provider == "openai":
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required when RECEIPT_OCR_PROVIDER=openai.")
        return OpenAIVisionOCRProvider(settings.openai_api_key, settings.openai_model)
    raise RuntimeError(f"Unsupported OCR provider: {settings.ocr_provider}")
