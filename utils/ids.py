import uuid


def generate_chunk_id(
    file_name,
    chunk_index: int,
) -> str:

    value = (
        f"{file_name}:"
        f"{chunk_index}"
    )

    return str(
        uuid.uuid5(
            uuid.NAMESPACE_URL,
            value,
        )
    )