from typing import Annotated

from pydantic import AfterValidator
from pydantic import StringConstraints

from pcapi.core.categories.genres import music
from pcapi.core.categories.genres import show
from pcapi.core.providers import constants


NameString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1024)]
GtlIdString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=128)]

# could probably be a little bit more strict, but let's be safe for now
VisaString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=8, max_length=64)]

EanString = Annotated[str, AfterValidator(lambda s: len(s) in (8, 13, 128))]

MusicType = Annotated[int, AfterValidator(lambda t: t in music.MUSIC_SLUG_BY_GTL_ID)]
MusicSubType = Annotated[int, AfterValidator(lambda t: t in music.MUSIC_SUB_TYPES_BY_SLUG)]

ShowType = Annotated[int, AfterValidator(lambda t: t in show.SHOW_TYPES_LABEL_BY_CODE)]
ShowSubType = Annotated[int, AfterValidator(lambda t: t in show.SHOW_SUB_TYPES_BY_CODE)]

TiteliveMusicGenres = Annotated[str, AfterValidator(lambda g: g in constants.TITELIVE_MUSIC_GENRES_BY_GTL_ID)]
