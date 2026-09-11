"""Validate ZIP members before extraction; never execute uploaded source code."""

import re
import stat
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from fastapi import UploadFile

from backend.app.config import Settings
from backend.app.errors import AppError

RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}
IGNORED = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", "__MACOSX"}


def read_sidecar(upload: UploadFile | None, suffixes: set[str], limit: int) -> str | None:
    if upload is None:
        return None
    if Path(upload.filename or "").suffix.lower() not in suffixes:
        raise AppError(422, "invalid_file_type", f"Expected one of: {', '.join(sorted(suffixes))}.")
    content = upload.file.read(limit + 1)
    if len(content) > limit:
        raise AppError(413, "file_too_large", "Requirements or mappings file exceeds the configured limit.")
    try:
        return content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise AppError(422, "invalid_encoding", "Requirements and mappings must use UTF-8.") from exc


def extract_repository(upload: UploadFile, workspace: Path, settings: Settings) -> Path:
    if not (upload.filename or "").lower().endswith(".zip"):
        raise AppError(422, "invalid_file_type", "Repository must be a .zip file.")
    archive = workspace / "upload.zip"
    size = 0
    with archive.open("xb") as destination:
        while chunk := upload.file.read(1024 * 1024):
            size += len(chunk)
            if size > settings.max_upload_bytes:
                raise AppError(413, "upload_too_large", "Repository ZIP exceeds the configured upload limit.")
            destination.write(chunk)
    root = (workspace / "repository").resolve()
    root.mkdir()
    actual_size = 0
    names = set()
    spellings = {}
    try:
        with ZipFile(archive) as zipped:
            members = zipped.infolist()
            if len(members) > settings.max_files:
                raise AppError(413, "too_many_files", "Repository contains too many ZIP entries.")
            if sum(member.file_size for member in members) > settings.max_extracted_bytes:
                raise AppError(413, "archive_too_large", "Uncompressed repository exceeds the configured limit.")
            for member in members:
                name = member.filename
                parts = name.rstrip("/").split("/")
                unsafe = (not name or "\x00" in member.orig_filename or name.startswith("/") or "\\" in member.orig_filename or any(
                    part in {"", ".", ".."} or part.endswith((".", " "))
                    or re.search(r'[<>:"|?*\x00-\x1f]', part)
                    or part.split(".")[0].upper() in RESERVED for part in parts
                ))
                if unsafe:
                    raise AppError(422, "unsafe_archive", "ZIP contains an unsafe or non-portable path.")
                mode = stat.S_IFMT(member.external_attr >> 16)
                if mode not in {0, stat.S_IFREG, stat.S_IFDIR} or member.flag_bits & 1:
                    raise AppError(422, "unsafe_archive", "Links, special files, and encrypted ZIP entries are unsupported.")
                normalized = "/".join(parts).casefold()
                if normalized in names:
                    raise AppError(422, "unsafe_archive", "ZIP contains duplicate or case-colliding paths.")
                names.add(normalized)
                for length in range(1, len(parts) + 1):
                    prefix = "/".join(parts[:length])
                    previous = spellings.setdefault(prefix.casefold(), prefix)
                    if previous != prefix:
                        raise AppError(422, "unsafe_archive", "ZIP contains case-colliding paths.")
                # Check ignored paths for safety too, but do not send them to parsers.
                if any(part in IGNORED for part in parts):
                    continue
                destination = root.joinpath(*parts).resolve()
                if not destination.is_relative_to(root):
                    raise AppError(422, "unsafe_archive", "ZIP entry escapes the extraction directory.")
                if member.is_dir():
                    destination.mkdir(parents=True, exist_ok=True)
                    continue
                destination.parent.mkdir(parents=True, exist_ok=True)
                with zipped.open(member) as source, destination.open("xb") as output:
                    while chunk := source.read(1024 * 1024):
                        actual_size += len(chunk)
                        if actual_size > settings.max_extracted_bytes:
                            raise AppError(413, "archive_too_large", "Uncompressed repository exceeds the configured limit.")
                        output.write(chunk)
    except (BadZipFile, NotImplementedError, RuntimeError, EOFError, ValueError, FileExistsError, NotADirectoryError) as exc:
        raise AppError(422, "invalid_archive", "ZIP is invalid, contains conflicting paths, or uses unsupported compression.") from exc
    supported_exts = {".py", ".js", ".jsx", ".ts", ".tsx"}
    has_source = any(f.suffix.lower() in supported_exts for f in root.rglob("*") if f.is_file())
    if not has_source:
        raise AppError(422, "no_source_files", "This prototype requires at least one supported source file (.py, .js, .ts, .jsx, .tsx).")
    children = list(root.iterdir())
    return children[0] if len(children) == 1 and children[0].is_dir() else root
