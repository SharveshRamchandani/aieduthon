from __future__ import annotations

import re
from typing import Any, Dict, List

from jsonschema import Draft7Validator, ValidationError

SLIDE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "slides": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "maxLength": 100},
                    "bullets": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 6,
                        "items": {"type": "string", "maxLength": 80},
                    },
                    "notes": {"type": "string"},
                    "images": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "caption": {"type": "string"},
                            },
                        },
                    },
                },
                "required": ["title", "bullets"],
            },
        }
    },
    "required": ["slides"],
}

_validator = Draft7Validator(SLIDE_SCHEMA)


class SlideValidationError(Exception):
    """Raised when slide JSON fails structural validation."""


def clean_text(text: str | None) -> str:
    """Remove markdown/code artifacts and normalise whitespace."""
    if not text:
        return ""
    cleaned = text
    cleaned = re.sub(r"(?i)\bNotes:\s*", "", cleaned)
    cleaned = re.sub(r"```[a-zA-Z]*", "", cleaned)
    cleaned = re.sub(r"^\s*[\{\}\[\]]\s*$", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r'^\s*"[A-Za-z0-9_ ]+"\s*:\s*[\[\{]\s*$', "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\n\s*\n+", "\n\n", cleaned)
    cleaned = cleaned.strip()
    return cleaned


def _truncate_words(text: str, limit: int = 12) -> str:
    words = text.split()
    if len(words) <= limit:
        return text
    return " ".join(words[:limit])


def _fallback_bullets(source: str) -> List[str]:
    """Derive bullets from free-form text when the model omits them."""
    if not source:
        return ["Key insight"]
    parts = re.split(r"[.;–—-]", source)
    bullets: List[str] = []
    for fragment in parts:
        cleaned = clean_text(fragment)
        if not cleaned:
            continue
        bullets.append(_truncate_words(cleaned))
        if len(bullets) >= 3:
            break
    return bullets or ["Key insight"]


def _sanitize_images(images: List[Dict[str, Any]] | None) -> List[Dict[str, str]]:
    sanitized: List[Dict[str, str]] = []
    if not images:
        return sanitized
    for img in images:
        if not isinstance(img, dict):
            continue
        caption = clean_text(img.get("caption") or img.get("id") or "")
        entry: Dict[str, str] = {}
        if img.get("id"):
            entry["id"] = clean_text(str(img["id"]))
        if caption:
            entry["caption"] = _truncate_words(caption, 20)
        if entry:
            sanitized.append(entry)
    return sanitized[:3]


def _normalize_bullets(raw_bullets: List[str] | None, fallback_source: str) -> List[str]:
    bullets: List[str] = []
    if raw_bullets:
        for bullet in raw_bullets:
            text = clean_text(bullet)
            if not text:
                continue
            bullets.append(_truncate_words(text))
            if len(bullets) == 6:
                break
    if not bullets:
        bullets = _fallback_bullets(fallback_source)
    return bullets


def _sanitize_slide(slide: Dict[str, Any]) -> Dict[str, Any]:
    title = clean_text(slide.get("title", "Slide"))[:100]
    notes = clean_text(slide.get("notes", ""))
    bullets = _normalize_bullets(slide.get("bullets"), notes or title)
    images = _sanitize_images(slide.get("images"))
    return {
        "title": title or "Slide",
        "bullets": bullets,
        "notes": notes,
        "images": images,
    }


def sanitize_slide_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and clean the slide JSON payload."""
    if not isinstance(payload, dict) or "slides" not in payload:
        raise SlideValidationError("Slide payload must contain a 'slides' array.")
    sanitized_slides = [_sanitize_slide(slide) for slide in payload.get("slides", [])]
    sanitized_payload = {"slides": sanitized_slides}
    errors = sorted(_validator.iter_errors(sanitized_payload), key=lambda e: e.path)
    if errors:
        messages = [f"{'/'.join(map(str, err.path)) or 'root'}: {err.message}" for err in errors]
        raise SlideValidationError("; ".join(messages))
    return sanitized_payload

