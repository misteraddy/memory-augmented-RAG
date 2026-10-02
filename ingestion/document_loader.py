from pathlib import Path

import fitz


class PDFDocumentLoader:

    def load(self, file_path: str) -> list[dict]:
        document = fitz.open(file_path)

        pages = []

        try:
            for page_number, page in enumerate(document, start=1):
                text = page.get_text("text").strip()

                if not text:
                    continue

                pages.append(
                    {
                        "page_number": page_number,
                        "text": text,
                    }
                )

        finally:
            document.close()

        return pages