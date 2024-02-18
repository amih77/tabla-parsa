import os

from dataclasses import dataclass, field
from bs4 import BeautifulSoup

from odm_models.document import Document
from utils.common import DocumentType


@dataclass
class HTMLParser:
    file_path: str
    soup: BeautifulSoup = field(init=False)

    def __post_init__(self):
        with open(self.file_path, "r", encoding="utf-8") as file:
            html_content = file.read()
        self.soup = BeautifulSoup(html_content, "html.parser")

    def parse(self) -> Document:
        values, row_headers = self.parse_values()

        return Document(
            **{
                "type": DocumentType.HTML,
                "title": self.parse_title(),
                "col_headers": self.parse_col_headers(),
                "values": values,
                "row_headers": row_headers,
                "footer": self.parse_footer(),
                "path": self.file_path,
            }
        )

    def parse_title(self) -> str | None:
        return self.soup.caption.text.strip() if self.soup.caption else None

    def parse_col_headers(self) -> list[str] | None:
        if not self.soup.thead:
            return None
        headers = [th.get_text(strip=True) for th in self.soup.thead.find_all("th")]
        if len(headers) > 1:
            return [th.get_text(strip=True) for th in self.soup.thead.find_all("th")][
                1:
            ]
        return None

    def parse_footer(self) -> str | None:
        return self.soup.tfoot.tr.td.get_text(strip=True) if self.soup.tfoot else None

    def parse_values(self) -> tuple[list[list[tuple[float, str | None]]], list[str]]:
        body_rows_raw = [
            [td.get_text(strip=True) for td in tr.find_all("td")]
            for tr in self.soup.tbody.find_all("tr")
        ]
        row_headers = [body_row[0] for body_row in body_rows_raw]
        values = [
            [
                (float(val[:-1]), "%") if val.endswith("%") else (float(val), None)
                for val in body_row[1:]
            ]
            for body_row in body_rows_raw
        ]
        return values, row_headers
