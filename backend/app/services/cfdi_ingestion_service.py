"""Ingesta de CFDI desde múltiples fuentes."""

from __future__ import annotations

from email import message_from_bytes
from pathlib import Path
from typing import Iterable


class CFDIIngestionService:
    """Orquesta la recepción de XML CFDI en bruto."""

    def from_local_folder(self, folder: str) -> list[str]:
        return self._read_xml_files(Path(folder).glob("*.xml"))

    def from_sat_sync_folder(self, folder: str) -> list[str]:
        return self._read_xml_files(Path(folder).glob("**/*.xml"))

    def from_manual_upload(self, xml_content: str) -> list[str]:
        return [xml_content]

    def from_api_payload(self, payload: dict) -> list[str]:
        xml_docs = payload.get("xml_documents", [])
        return [doc for doc in xml_docs if isinstance(doc, str) and doc.strip()]

    def from_email_bytes(self, raw_email: bytes) -> list[str]:
        msg = message_from_bytes(raw_email)
        xmls: list[str] = []
        for part in msg.walk():
            filename = part.get_filename() or ""
            if filename.lower().endswith(".xml"):
                payload = part.get_payload(decode=True) or b""
                xmls.append(payload.decode("utf-8", errors="ignore"))
        return xmls

    def _read_xml_files(self, paths: Iterable[Path]) -> list[str]:
        docs: list[str] = []
        for file_path in paths:
            docs.append(file_path.read_text(encoding="utf-8"))
        return docs
