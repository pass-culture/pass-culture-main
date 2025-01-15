import pytest

from pcapi.core.artist.utils import sanitize_author_html


class SanitizeAuthorHtmlTest:
    @pytest.mark.parametrize(
        "html, sanitized_html",
        [
            (
                '<bdi><a href="https://www.wikidata.org/wiki/Q56009715" class="extiw" title="d:Q56009715"><span title="office assisting the president of India">President\'s Secretariat</span></a></bdi>',
                '<a href="https://www.wikidata.org/wiki/Q56009715">President\'s Secretariat</a>',
            ),
            (
                '<a href="//www.flickr.com/people/92359345@N07" class="extiw" title="flickruser:92359345@N07">Prime Minister\'s Office, Government of India</a>',
                '<a href="//www.flickr.com/people/92359345@N07">Prime Minister\'s Office, Government of India</a>',
            ),
            (
                "India Post, Government of India",
                "India Post, Government of India",
            ),
        ],
    )
    def test_sanitize_author_html(self, html, sanitized_html):
        assert sanitize_author_html(html) == sanitized_html
