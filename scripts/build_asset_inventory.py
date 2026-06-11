from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ORIGINALS = ROOT / "original assets"
STAGING = ROOT / ".asset-staging" / "extracted"
DATA = ROOT / "data"
PRODUCT_ASSETS = ROOT / "assets" / "products"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ARCHIVE_EXTENSIONS = {".zip", ".rar"}


PART_PATTERNS = [
    re.compile(r"\b\d{2,3}[A-Z]?-\d{3,5}\b", re.IGNORECASE),
    re.compile(r"\b\d[A-Z]-?\d{4}\b", re.IGNORECASE),
    re.compile(r"\b\d[A-Z]\d{4}\b", re.IGNORECASE),
    re.compile(r"\bC\d{1,2}[A-Z]?\b", re.IGNORECASE),
    re.compile(r"\b34\d{2}[A-Z]\b", re.IGNORECASE),
]

NOISE_TOKENS = {
    "IMG",
    "JPEG",
    "JPG",
    "PNG",
    "COPY",
    "VIDEOSHOT",
    "WECHAT",
}


@dataclass
class AssetRow:
    asset_id: str
    source_path: str
    normalized_path: str
    sha256: str
    duplicate_of: str
    file_name: str
    extension: str
    file_size_bytes: int
    width: int | None
    height: int | None
    part_number: str
    part_number_source: str
    recognition_confidence: str
    product_description: str
    category: str
    image_quality: str
    visible_flaws: str
    suggested_edit_prompt: str
    cat_fitment_status: str
    cat_fitment_summary: str
    cat_fitment_sources: str
    selected_for_site: bool
    web_asset_path: str


def normalize_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_slug(value: str) -> str:
    value = value.strip().upper()
    value = re.sub(r"[^A-Z0-9-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "UNIDENTIFIED"


def extract_archives() -> list[dict[str, str]]:
    STAGING.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, str]] = []
    for archive in ORIGINALS.rglob("*"):
        if not archive.is_file() or archive.suffix.lower() not in ARCHIVE_EXTENSIONS:
            continue
        result = {
            "archive_path": normalize_path(archive),
            "extension": archive.suffix.lower(),
            "status": "pending",
            "output_dir": "",
            "note": "",
        }
        if archive.suffix.lower() == ".zip":
            output_dir = STAGING / safe_slug(archive.stem)
            output_dir.mkdir(parents=True, exist_ok=True)
            try:
                with zipfile.ZipFile(archive) as zf:
                    zf.extractall(output_dir)
                result["status"] = "extracted"
                result["output_dir"] = normalize_path(output_dir)
            except Exception as exc:  # noqa: BLE001
                result["status"] = "failed"
                result["note"] = str(exc)
        else:
            result["status"] = "needs_external_extractor"
            result["note"] = "RAR extraction requires 7-Zip/WinRAR or another extractor."
        results.append(result)
    return results


def extract_part_number(path: Path) -> tuple[str, str, str]:
    text = " ".join(path.parts[-5:])
    cleaned = text.replace("_", " ").replace("(", " ").replace(")", " ")
    matches: list[str] = []
    for pattern in PART_PATTERNS:
        matches.extend(match.group(0).upper().replace(" ", "") for match in pattern.finditer(cleaned))
    filtered = []
    for match in matches:
        if match in NOISE_TOKENS:
            continue
        if re.fullmatch(r"20\d{6,}", match):
            continue
        filtered.append(match)
    if not filtered:
        return "", "none", "unreadable"
    part = filtered[0]
    confidence = "high" if "-" in part or re.fullmatch(r"\d[A-Z]-?\d{4}", part) else "medium"
    return part, "filename", confidence


def infer_category(path: Path, part_number: str) -> tuple[str, str]:
    text = " ".join(path.parts).lower()
    if any(token in text for token in ["发电", "generator", "genset", "alternator"]):
        return "Generator Set Parts", "Generator set or power-system related asset."
    if any(
        token in text
        for token in [
            "喷油",
            "injector",
            "油泵",
            "pump",
            "活塞",
            "piston",
            "缸盖",
            "cylinder",
            "缸垫",
            "gasket",
            "密封",
            "seal",
            "排气门",
            "valve",
            "火花塞",
            "spark",
            "传感器",
            "sensor",
            "filter",
            "c15",
            "c18",
            "c32",
            "3412",
        ]
    ):
        return "Engine Parts", "Diesel engine component or related replacement part."
    if any(token in text for token in ["矿", "mining", "truck", "undercarriage", "track"]):
        return "Mining Machine Parts", "Mining or heavy-duty machine component."
    if any(token in text for token in ["轮", "wheel", "bucket", "excavator", "loader", "grader", "推土"]):
        return "Engineering / Construction Machinery", "Construction machinery component."
    if part_number:
        return "Needs Review", "CAT-compatible part number detected; application needs fitment confirmation."
    return "Needs Review", "Product type requires visual review."


def score_quality(path: Path, width: int | None, height: int | None) -> tuple[str, str, str]:
    flaws: list[str] = []
    lower_name = path.name.lower()
    if "videoshot" in lower_name:
        flaws.append("video frame capture")
    if "微信" in path.name or "wechat" in lower_name:
        flaws.append("social app source name")
    if width is None or height is None:
        return "unreadable", "Cannot read image dimensions.", "Do not use until the file can be opened."
    short_edge = min(width, height)
    long_edge = max(width, height)
    if short_edge < 700:
        quality = "low"
        flaws.append("low resolution")
    elif long_edge >= 1800 and short_edge >= 1000:
        quality = "high"
    else:
        quality = "medium"
    edit_prompt = (
        "Clean the product photo while preserving the exact part: crop to the part, remove distracting background "
        "clutter, correct exposure and white balance, keep labels and part-number markings legible, avoid changing "
        "the physical product shape, and output a realistic catalog-ready industrial product image."
    )
    return quality, "; ".join(flaws), edit_prompt


def image_dimensions(path: Path) -> tuple[int | None, int | None]:
    try:
        with Image.open(path) as image:
            return image.width, image.height
    except Exception:  # noqa: BLE001
        return None, None


def write_web_image(source: Path, target: Path) -> None:
    with Image.open(source) as image:
        image.thumbnail((1400, 1400), Image.Resampling.LANCZOS)
        if image.mode in {"RGBA", "LA"}:
            background = Image.new("RGB", image.size, "white")
            alpha = image.getchannel("A") if "A" in image.getbands() else None
            background.paste(image, mask=alpha)
            output = background
        else:
            output = image.convert("RGB")
        output.save(target, "JPEG", quality=84, optimize=True, progressive=True)


def iter_candidate_files() -> list[Path]:
    paths = [p for p in ORIGINALS.rglob("*") if p.is_file()]
    if STAGING.exists():
        paths.extend(p for p in STAGING.rglob("*") if p.is_file())
    return sorted(paths, key=lambda p: normalize_path(p).lower())


def build_inventory() -> list[AssetRow]:
    DATA.mkdir(parents=True, exist_ok=True)
    PRODUCT_ASSETS.mkdir(parents=True, exist_ok=True)
    seen_hashes: dict[str, str] = {}
    selected_parts: set[str] = set()
    rows: list[AssetRow] = []

    for path in iter_candidate_files():
        extension = path.suffix.lower()
        if extension not in IMAGE_EXTENSIONS and extension not in ARCHIVE_EXTENSIONS and extension != ".psd":
            continue
        file_hash = sha256_file(path)
        duplicate_of = seen_hashes.get(file_hash, "")
        if not duplicate_of:
            seen_hashes[file_hash] = normalize_path(path)

        width = height = None
        part_number = ""
        part_source = "none"
        confidence = "unreadable"
        category = "Needs Review"
        description = "Non-image asset; not eligible for product display."
        quality = "not_applicable"
        flaws = ""
        edit_prompt = ""
        selected = False
        web_asset_path = ""

        if extension in IMAGE_EXTENSIONS:
            width, height = image_dimensions(path)
            part_number, part_source, confidence = extract_part_number(path)
            category, description = infer_category(path, part_number)
            quality, flaws, edit_prompt = score_quality(path, width, height)
            if (
                part_number
                and not duplicate_of
                and confidence in {"high", "medium"}
                and quality in {"high", "medium"}
                and part_number not in selected_parts
            ):
                selected = True
                selected_parts.add(part_number)
                part_slug = safe_slug(part_number)
                target_dir = PRODUCT_ASSETS / part_slug
                target_dir.mkdir(parents=True, exist_ok=True)
                target_name = f"{part_slug}.jpg"
                target = target_dir / target_name
                write_web_image(path, target)
                web_asset_path = normalize_path(target)

        asset_id = hashlib.sha1(normalize_path(path).encode("utf-8")).hexdigest()[:12]
        rows.append(
            AssetRow(
                asset_id=asset_id,
                source_path=normalize_path(path),
                normalized_path=normalize_path(path),
                sha256=file_hash,
                duplicate_of=duplicate_of,
                file_name=path.name,
                extension=extension,
                file_size_bytes=path.stat().st_size,
                width=width,
                height=height,
                part_number=part_number,
                part_number_source=part_source,
                recognition_confidence=confidence,
                product_description=description,
                category=category,
                image_quality=quality,
                visible_flaws=flaws,
                suggested_edit_prompt=edit_prompt,
                cat_fitment_status="pending_lookup" if part_number else "no_part_number",
                cat_fitment_summary="",
                cat_fitment_sources="",
                selected_for_site=selected,
                web_asset_path=web_asset_path,
            )
        )
    return rows


def write_outputs(rows: list[AssetRow], archive_results: list[dict[str, str]]) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    fieldnames = list(asdict(rows[0]).keys()) if rows else [field.name for field in AssetRow.__dataclass_fields__.values()]
    csv_path = DATA / "assets.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))
    json_path = DATA / "assets.json"
    json_path.write_text(json.dumps([asdict(row) for row in rows], ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA / "archive_extraction.json").write_text(
        json.dumps(archive_results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    selected = [row for row in rows if row.selected_for_site]
    selected_path = DATA / "selected-products.json"
    selected_path.write_text(json.dumps([asdict(row) for row in selected], ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    archive_results = extract_archives()
    rows = build_inventory()
    write_outputs(rows, archive_results)
    print(f"Assets indexed: {len(rows)}")
    print(f"Selected for site: {sum(1 for row in rows if row.selected_for_site)}")
    print("Wrote data/assets.csv, data/assets.json, data/selected-products.json")


if __name__ == "__main__":
    main()
