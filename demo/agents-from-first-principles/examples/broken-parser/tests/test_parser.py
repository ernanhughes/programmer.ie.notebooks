from parser import split_record


def test_default_comma_delimiter() -> None:
    assert split_record("A,B,C") == ["A", "B", "C"]


def test_pipe_delimiter() -> None:
    assert split_record("A|B|C", "|") == ["A", "B", "C"]
