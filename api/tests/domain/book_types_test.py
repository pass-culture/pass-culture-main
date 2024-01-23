import re

from pcapi.core.providers.titelive_gtl import GTLS
from pcapi.domain.book_types import book_types


class BookTypesTest:
    def _code_matches_level(self, gtl):
        greater_than_zero_re = r"([0-9][1-9]|[1-9]0)"
        zero_re = r"00"
        return re.match(greater_than_zero_re * gtl.level + zero_re * (4 - gtl.level), gtl.code) is not None

    def _is_child(self, child, parent):
        return child.startswith(parent.rstrip("0"))

    def test_book_types_are_included_in_gtls(self):
        gtl_codes = set(GTLS.keys())
        book_types_codes = {gtl.code for book_type in book_types for gtl in book_type.gtls}
        book_subtypes_codes = {
            gtl.code for book_type in book_types for book_subtype in book_type.children for gtl in book_subtype.gtls
        }
        all_book_codes = book_types_codes | book_subtypes_codes

        assert all_book_codes < gtl_codes

    def test_book_types_labels_match_titelive_labels(self):
        book_types_gtls = [gtl for book_type in book_types for gtl in book_type.gtls]
        book_subtypes_gtls = [
            gtl for book_type in book_types for book_subtype in book_type.children for gtl in book_subtype.gtls
        ]
        all_book_gtls = book_types_gtls + book_subtypes_gtls

        assert all(gtl.label == GTLS[gtl.code]["label"] for gtl in all_book_gtls)

    def test_book_types_positions_are_consistent(self):
        assert list(range(1, len(book_types) + 1)) == sorted([book_type.position for book_type in book_types])
        for book_type in book_types:
            assert list(range(1, len(book_type.children) + 1)) == sorted(
                [child.position for child in book_type.children]
            )

    def test_gtl_codes_match_level(self):
        for book_type in book_types:
            assert all(self._code_matches_level(gtl) for gtl in book_type.gtls)
            assert all(self._code_matches_level(gtl) for subtype in book_type.children for gtl in subtype.gtls)

    def test_gtl_in_booksubtype_is_included_in_booktype_gtls(self):
        assert all(
            any(self._is_child(sub_gtl.code, gtl.code) for gtl in book_type.gtls)
            for book_type in book_types
            for subtype in book_type.children
            for sub_gtl in subtype.gtls
        )
