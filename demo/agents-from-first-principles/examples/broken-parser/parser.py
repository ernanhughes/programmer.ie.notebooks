def split_record(text: str, delimiter: str = ",") -> list[str]:
    """Split one record into fields.

    The implementation is deliberately wrong for the capstone: it ignores
    the caller-supplied delimiter and always splits on a comma.
    """

    return text.split(",")
