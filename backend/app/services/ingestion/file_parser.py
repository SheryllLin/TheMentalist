"""
FileParser — extracts plain text and/or structured data from uploaded files.

Supported formats:
  TXT   → raw text
  PDF   → pdfplumber
  DOCX  → python-docx
  CSV   → pandas (returns list of dicts)
  JSON  → standard library

For CSV/JSON with a known schema (CDR, transactions), the parser identifies the
schema and returns structured rows instead of converting everything to text.
This avoids unnecessarily sending tabular data to an LLM.
"""
import csv
import io
import json
import os
from typing import Union

import pandas as pd


class ParsedDocument:
    def __init__(
        self,
        raw_text: str = "",
        structured_rows: list[dict] | None = None,
        schema_type: str | None = None,
    ):
        self.raw_text = raw_text
        # structured_rows is set for CSV/JSON with a detectable schema
        self.structured_rows = structured_rows or []
        # schema_type: "CDR" | "TRANSACTIONS" | "GENERIC_CSV" | "GENERIC_JSON" | None
        self.schema_type = schema_type


# Column sets that identify known structured schemas
_CDR_COLUMNS = {"caller", "receiver", "timestamp", "duration_sec", "cell_tower"}
_TRANSACTION_COLUMNS = {
    "sender_account", "receiver_account", "amount", "timestamp", "transaction_type"
}


class FileParser:

    @staticmethod
    def parse(file_path: str, filename: str) -> ParsedDocument:
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".txt":
            return FileParser._parse_txt(file_path)
        elif ext == ".pdf":
            return FileParser._parse_pdf(file_path)
        elif ext == ".docx":
            return FileParser._parse_docx(file_path)
        elif ext == ".csv":
            return FileParser._parse_csv(file_path)
        elif ext == ".json":
            return FileParser._parse_json(file_path)
        else:
            return ParsedDocument(raw_text="[Unsupported file type]")

    @staticmethod
    def _parse_txt(path: str) -> ParsedDocument:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return ParsedDocument(raw_text=f.read())

    @staticmethod
    def _parse_pdf(path: str) -> ParsedDocument:
        try:
            import pdfplumber
            text_parts = []
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text_parts.append(extracted)
            return ParsedDocument(raw_text="\n\n".join(text_parts))
        except ImportError:
            return ParsedDocument(raw_text="[pdfplumber not installed — PDF parsing unavailable]")
        except Exception as e:
            return ParsedDocument(raw_text=f"[PDF parse error: {e}]")

    @staticmethod
    def _parse_docx(path: str) -> ParsedDocument:
        try:
            from docx import Document as DocxDocument
            doc = DocxDocument(path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return ParsedDocument(raw_text="\n".join(paragraphs))
        except ImportError:
            return ParsedDocument(raw_text="[python-docx not installed]")
        except Exception as e:
            return ParsedDocument(raw_text=f"[DOCX parse error: {e}]")

    @staticmethod
    def _parse_csv(path: str) -> ParsedDocument:
        try:
            df = pd.read_csv(path)
            columns = set(df.columns.str.lower().tolist())

            # Detect schema
            if _CDR_COLUMNS.issubset(columns):
                schema = "CDR"
            elif _TRANSACTION_COLUMNS.issubset(columns):
                schema = "TRANSACTIONS"
            else:
                schema = "GENERIC_CSV"

            rows = df.to_dict(orient="records")
            # Also produce a text representation for the LLM context
            text = f"[Structured data — schema: {schema}]\n{df.to_string(index=False)}"
            return ParsedDocument(raw_text=text, structured_rows=rows, schema_type=schema)
        except Exception as e:
            return ParsedDocument(raw_text=f"[CSV parse error: {e}]")

    @staticmethod
    def _parse_json(path: str) -> ParsedDocument:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                rows = data
                columns = set(rows[0].keys()) if rows else set()
                if _CDR_COLUMNS.issubset(columns):
                    schema = "CDR"
                elif _TRANSACTION_COLUMNS.issubset(columns):
                    schema = "TRANSACTIONS"
                else:
                    schema = "GENERIC_JSON"
                text = f"[Structured JSON data — {len(rows)} records, schema: {schema}]"
            else:
                rows = [data]
                schema = "GENERIC_JSON"
                text = json.dumps(data, indent=2)
            return ParsedDocument(raw_text=text, structured_rows=rows, schema_type=schema)
        except Exception as e:
            return ParsedDocument(raw_text=f"[JSON parse error: {e}]")
