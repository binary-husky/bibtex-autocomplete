from pathlib import Path
from typing import Iterator, List, Optional, Tuple

import pytest

from bibtexautocomplete.bibtex.author import Author
from bibtexautocomplete.bibtex.base_field import (
    FIELD_NO_MATCH,
    StrictStringField,
    listify,
)
from bibtexautocomplete.bibtex.entry import (
    BibtexEntry,
    FieldNames,
    FieldNamesSet,
    SpecialFields,
)
from bibtexautocomplete.bibtex.fields import URLField
from bibtexautocomplete.bibtex.io import file_read, write
from bibtexautocomplete.bibtex.matching import CERTAIN_MATCH, NO_MATCH, match_score
from bibtexautocomplete.bibtex.normalize import (
    EN_MONTHS,
    normalize_doi,
    normalize_month,
    normalize_str,
    normalize_str_weak,
    normalize_url,
)

tests = [
    ("abc", "abc"),
    ("a.b.c", "a.b.c"),
    ("a  b\t\n\rc\nd", "a b c d"),
    ("ABC", "abc"),
    ("12 +*-/#.?:$%", "12 +*-/#.?:$%"),
    ("àbcéèçôêâû+ÏÖÜÉÀÈÇÉ#!;§", "abceecoeau+ioueaece#!;§"),
]


@pytest.mark.parametrize(("inp", "out"), tests)
def test_normalize_str_weak(inp: str, out: str) -> None:
    assert normalize_str_weak(inp) == out


tests = [
    ("abc", "abc"),
    ("a.b.c", "a b c"),
    ("a  b\t\n\rc\nd", "a b c d"),
    ("ABC", "abc"),
    ("12 +*-/#.?:$%", "12"),
    ("àbcéèçôêâû+ÏÖÜÉÀÈÇÉ#!;§", "abceecoeau ioueaece"),
]


@pytest.mark.parametrize(("inp", "out"), tests)
def test_normalize_str(inp: str, out: str) -> None:
    assert normalize_str(inp) == out


def test_normalize_doi() -> None:
    doi = [
        "10.1000/123456",
        "10.1038/issn.1476-4687",
        "10.1111/dome.1208",
        "10.1111/josi.12122",
    ]
    prefixes = ["", "https://www.doi.org/", "https://somedomain.com/some/path/"]
    for d in doi:
        for p in prefixes:
            assert normalize_doi(p + d) == d


def test_normalize_month() -> None:
    for month, norm in EN_MONTHS.items():
        assert normalize_month(month) == str(norm)
    for month in ("bla", "not.a.month", "6496489", "#!!0"):
        assert normalize_month(month) == month


def io_test(file: str) -> None:
    db = file_read(Path(file))
    write(db)


def test_case() -> None:
    db = file_read(Path("tests/test_0.bib"))
    assert "author" in db.entries[0]


def test_io_0() -> None:
    io_test("tests/test_0.bib")


def test_io_1() -> None:
    io_test("tests/test_1.bib")


authors = [
    ("John Jones", [Author("Jones", "John")]),
    (
        "Lewis, C. S. and Douglas Adams",
        [Author("Lewis", "C. S."), Author("Adams", "Douglas")],
    ),
    (
        "Martin Luther King and M. L. King",
        [Author("King", "Martin Luther"), Author("King", "M. L.")],
    ),
    ("", []),
    (
        "Peter Müller 0001 and Joakim von Wright",
        [Author("Müller", "Peter"), Author("von Wright", "Joakim")],
    ),
]


@pytest.mark.parametrize(("author", "res"), authors)
def test_get_authors(author: str, res: List[Author]) -> None:
    assert Author.from_namelist(author) == res


def test_BibtexEntry_normal() -> None:
    a = BibtexEntry()
    for field in FieldNamesSet - SpecialFields:
        assert getattr(a, field) is None
        setattr(a, field, field)
    for field in FieldNamesSet - SpecialFields:
        assert getattr(a, field) == field


def test_BibtexEntry_special() -> None:
    a = BibtexEntry({})
    for field in SpecialFields:
        val = getattr(a, field)
        if field in ("author", "editor"):
            assert val == []
            setattr(a, field, [])
        else:
            assert val is None
            setattr(a, field, None)


@pytest.mark.parametrize(("author", "res"), authors)
def test_BibtexEntry_author_get(author: str, res: List[Author]) -> None:
    b = BibtexEntry({FieldNames.AUTHOR: author})
    assert b.author == res


@pytest.mark.parametrize(("author", "res"), authors)
def test_BibtexEntry_editor_get(author: str, res: List[Author]) -> None:
    b = BibtexEntry({FieldNames.EDITOR: author})
    assert b.editor == res


@pytest.mark.parametrize(("author", "res"), authors)
def test_BibtexEntry_author_set(author: str, res: List[Author]) -> None:
    b = BibtexEntry()
    b.author = res
    assert b.author == res


@pytest.mark.parametrize(("author", "res"), authors)
def test_BibtexEntry_editor_set(author: str, res: List[Author]) -> None:
    b = BibtexEntry()
    b.editor = res
    assert b.editor == res


def iterate_nested(list: List[List[str]]) -> Iterator[Tuple[int, str]]:
    """Iterate over a nested list, returning (index of sublist, element)"""
    for i, l in enumerate(list):
        for x in l:
            yield (i, x)


def test_matching() -> None:
    assert match_score(BibtexEntry(), BibtexEntry()) <= NO_MATCH
    doi1 = BibtexEntry({"doi": "10.1234/12345"})
    doi2 = BibtexEntry({"doi": "10.1234/different.12345"})
    assert match_score(doi1, doi1) >= CERTAIN_MATCH
    assert match_score(doi1, doi2) <= NO_MATCH
    # in same sublist should match (weakly)
    # in different sublists => no match
    titles = [
        ["My\tawesome paper!", "my awesome paper", "My AwESoMe Paper..."],
        ["My book, volume 1", "my book volume 1"],
        ["My book, volume 2"],
    ]
    authors = [
        ["Doe, J. and Smith, T.", "Doe, John", "John Doe", "Patrick, H. and Doe, J."],
        ["Henry, F."],
    ]
    for id, title in iterate_nested(titles):
        entry = BibtexEntry({"title": title})
        score_same = match_score(entry, entry)
        assert score_same >= NO_MATCH
        for id2, title2 in iterate_nested(titles):
            entry2 = BibtexEntry({"title": title2})
            score_diff = match_score(entry, entry2)
            assert score_same >= score_diff
            assert score_diff == match_score(entry2, entry)
            if id == id2:
                assert score_diff > NO_MATCH
            else:
                assert score_diff <= NO_MATCH

    title = "My Awesome paper"
    for id, author in iterate_nested(authors):
        entry = BibtexEntry({"title": title, "author": author})
        score_same = match_score(entry, entry)
        assert score_same >= NO_MATCH
        for id2, author2 in iterate_nested(authors):
            entry2 = BibtexEntry({"title": title, "author": author2})
            score_diff = match_score(entry, entry2)
            assert score_same >= score_diff
            assert score_diff == match_score(entry2, entry)
            if id == id2:
                print(author, author2)
                assert score_diff > NO_MATCH
            else:
                assert score_diff <= NO_MATCH

    entry = BibtexEntry({"title": title, "year": "2023"})
    entry2 = BibtexEntry({"title": title, "year": "2024"})
    entry3 = BibtexEntry({"title": title, "year": "Invalid"})
    assert match_score(entry, entry) > NO_MATCH
    assert match_score(entry, entry2) <= NO_MATCH
    assert match_score(entry, entry3) > NO_MATCH


urls: List[Tuple[str, Optional[Tuple[str, str]]]] = [
    ("http://google.com", ("google.com", "")),
    ("https://google.com", ("google.com", "")),
    ("https://google.com/path/to/something", ("google.com", "/path/to/something")),
    ("https://google.fr?query=hello", ("google.fr", "?query=hello")),
    ("https://google.fr/path/?query=hello", ("google.fr", "/path/?query=hello")),
    ("file:///home/user/thingy", None),
    ("NOT AN URL", None),
    ("http//sfdq.com/fp", None),
]


@pytest.mark.parametrize(("url", "result"), urls)
def test_normalize_url(url: str, result: Optional[Tuple[str, str]]) -> None:
    assert normalize_url(url) == result


urls2: List[Tuple[str, Optional[str]]] = [
    ("http://google.com", "https://google.com"),
    (
        "http://google.com?query=something+space",
        "https://google.com?query=something+space",
    ),
    (
        "http://google.com?query=something%20space",
        "https://google.com?query=something+space",
    ),
]


@pytest.mark.parametrize(("url", "result"), urls2)
def test_normalize_url2(url: str, result: Optional[str]) -> None:
    field = URLField("url", "test")
    assert field.normalize(url) == result


@listify(separator_regex=r",", separator=", ")
class ListString(StrictStringField):
    pass


listify_to_from: List[Tuple[str, Optional[str]]] = [
    ("", None),
    ("      ", None),
    (", , , , ", None),
    ("hello, my name  is,  fun", "hello, my name  is, fun"),
    ("a, b,  , c , d,", "a, b, c, d"),
]


@pytest.mark.parametrize(("source", "converted"), listify_to_from)
def test_listify_to_from(source: str, converted: Optional[str]) -> None:
    field = ListString("list_string", "test")
    field.set_str(source)
    assert field.to_str() == converted


listify_match_merge: List[Tuple[str, str, bool, Optional[str]]] = [
    ("a,b,c", "a,b,c", True, "a, b, c"),
    ("a,b,c", "d,e,f", False, None),
    ("a,b,d", "b,c,d", True, "a, b, c, d"),
    ("a,b,c", "b,d", True, "a, b, c, d"),
    ("b,d", "a,b,c", True, "a, b, c, d"),
    ("b,c,e", "a,b,d,e", True, "a, b, c, d, e"),
]


@pytest.mark.parametrize(("a", "b", "matches", "merged"), listify_match_merge)
def test_listify_match_merge(
    a: str, b: str, matches: bool, merged: Optional[str]
) -> None:
    field_a = ListString("list_string", "test")
    field_a.set_str(a)
    field_b = ListString("list_string", "test")
    field_b.set_str(b)
    score = field_a.matches(field_b)
    assert score is not None
    if matches:
        assert score > FIELD_NO_MATCH
        assert field_a.combine(field_b).to_str() == merged
    else:
        assert score <= FIELD_NO_MATCH
