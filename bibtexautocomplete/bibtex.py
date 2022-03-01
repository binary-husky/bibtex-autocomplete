"""
Functions to read/write/manipulate bibtex databases
"""

from typing import List, Optional

from bibtexparser import customization
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter

from .defs import EntryType

parser = BibTexParser()
# Keep non standard entries if present
parser.ignore_nonstandard_types = False

writer = BibTexWriter()
writer.indent = "\t"
writer.add_trailing_comma = True
writer.order_entries_by = ("author", "year", "title")
writer.display_order = ("author", "title")

PLAIN_PREFIX = "plain_"


def remove_plain_fields(entry: EntryType) -> None:
    """Removes the plain_ fields from an entry"""
    to_delete = [field for field in entry if field.startswith(PLAIN_PREFIX)]
    for to_del in to_delete:
        del entry[to_del]


def write(database: BibDatabase) -> str:
    """Transform the database to a bibtex string"""
    for entry in database.entries:
        remove_plain_fields(entry)
    return writer.write(database).strip()


def write_to(filepath, database: BibDatabase) -> None:
    output = write(database)
    if filepath is None:
        print(output)
    else:
        with open(filepath, "w") as file:
            file.write(output)


def read(filepath) -> BibDatabase:
    """reads the given file, parses and normalizes it"""
    # Read and parse the file
    with open(filepath, "r") as file:
        database = parser.parse_file(file)

    # Normalize bibliography
    for entry in database.entries:
        customization.convert_to_unicode(entry)
        customization.doi(entry)
        customization.link(entry)
        # adds plain_XXX for all fields, without nested braces
        customization.add_plaintext_fields(entry)

    return database


def update_plain_fields(entry: EntryType) -> None:
    """updates the plain fields on an entry"""
    remove_plain_fields(entry)
    customization.add_plaintext_fields(entry)


class Author:
    firstnames: Optional[str]
    lastname: str

    def __init__(self, lastname: str, firstnames: Optional[str]) -> None:
        self.lastname = lastname
        self.firstnames = firstnames

    def __repr__(self) -> str:
        return f"Author({self.lastname}, {self.firstnames})"

    def to_bibtex(self) -> str:
        if self.firstnames is not None:
            return f"{self.lastname}, {self.firstnames}"
        return self.lastname

    def __eq__(self, other) -> bool:
        return self.firstnames == other.firstnames and self.lastname == other.lastname


def get_authors(author: str) -> List[Author]:
    """Return a list of 'first name', 'last name' for authors"""
    authors = [author.strip() for author in author.replace("\n", " ").split(" and ")]
    formatted_authors = []
    for author in customization.getnames(authors):
        split = author.split(", ")
        formatted_authors.append(Author(split[0], split[1]))
    return formatted_authors


def has_field(entry: EntryType, field: str) -> bool:
    """Check if a given entry has non empty field"""
    return field in entry and entry[field] != ""


def get_entries(db: BibDatabase) -> List[EntryType]:
    return db.entries
