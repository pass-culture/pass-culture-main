from pcapi.core.providers.titelive_gtl import GTLS
from pcapi.domain.book_types import book_types


class BookTypesTest:
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
