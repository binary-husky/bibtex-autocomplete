from typing import Callable, Iterator, List

from bibtexparser.bibdatabase import BibDatabase

from .bibtex import get_entries, has_field
from .constants import EntryType, logger
from .lookup import AbstractBaseLookup
from .lookup_doi import CrossrefLookup, DBLPLookup


def memoize(attr_name: str):
    def decorator(function):
        def helper(self):
            if hasattr(self, attr_name):
                return getattr(self, attr_name)
            value = function(self)
            setattr(self, attr_name, value)
            return value


class BibtexAutocomplete:
    """Main class used to dispatch calls to the relevant lookups"""

    bibdatabases: List[BibDatabase]
    progress_doi: float = 0.0
    progress_url: float = 0.0

    DOI_lookups: List[Callable[[EntryType], AbstractBaseLookup]] = [
        CrossrefLookup,
        DBLPLookup,
    ]

    def iter_entries(self) -> Iterator[EntryType]:
        """Iterate through entries"""
        for db in self.bibdatabases:
            for entry in get_entries(db):
                yield entry
        raise StopIteration()

    @memoize("_total")
    def count_entries(self) -> int:
        """count the number of entries"""
        count = 0
        for db in self.bibdatabases:
            entries = get_entries(db)
            count += len(entries)
        return count

    def count_missing(self, field: str) -> int:
        """Counts the number of entries missing the given field"""
        count = 0
        for entry in self.iter_entries():
            if not has_field(entry, field):
                count += 1
        return count

    @memoize("_missing_dois")
    def count_missing_dois(self) -> int:
        """Counts the number of entries with missing dois"""
        return self.count_missing("doi")

    def get_dois(self) -> None:
        """Tries to find missing DOIs"""
        found = 0
        for entry in self.iter_entries():
            if has_field(entry, "doi"):
                continue
            for lookup in self.DOI_lookups:
                init = lookup(entry)
                res = init.query()
                if res is not None:
                    logger.info(f"Found DOI for {entry['ID']} : {res}")
                    entry["doi"] = res
                    found += 1
                    break
