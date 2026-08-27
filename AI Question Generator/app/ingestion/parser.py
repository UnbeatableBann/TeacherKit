from typing import Any

import pymupdf


class DocumentParser:
    def parse_pdf(self, file_bytes: bytes, filename: str) -> list[dict[str, Any]]:
        """
        Parses a PDF into pages and extracts text while trying to retain some structure.
        """
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
        pages = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text").strip()
            if text:
                pages.append(
                    {
                        "page_number": page_num + 1,
                        "text": text,
                        "source_location": f"page_{page_num + 1}",
                    }
                )
        return pages
