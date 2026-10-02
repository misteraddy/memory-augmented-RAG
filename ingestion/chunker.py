class TextChunker:

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 150,
    ):
        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size"
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_page(
        self,
        text: str,
        page_number: int,
    ) -> list[dict]:

        text = " ".join(text.split())

        chunks = []

        start = 0
        chunk_index = 0

        while start < len(text):

            end = min(
                start + self.chunk_size,
                len(text)
            )

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    {
                        "text": chunk_text,
                        "page_number": page_number,
                        "chunk_index": chunk_index,
                    }
                )

                chunk_index += 1

            if end >= len(text):
                break

            start = end - self.chunk_overlap

        return chunks

    def chunk_document(
        self,
        pages: list[dict],
    ) -> list[dict]:

        all_chunks = []

        global_chunk_index = 0

        for page in pages:

            page_chunks = self.chunk_page(
                text=page["text"],
                page_number=page["page_number"],
            )

            for chunk in page_chunks:

                chunk["chunk_index"] = global_chunk_index

                all_chunks.append(chunk)

                global_chunk_index += 1

        return all_chunks