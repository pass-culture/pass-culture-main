from pcapi.core.achievements.models import Achievement
from pcapi.core.achievements.models import AchievementType


FIRST_ADD_FAVORITE = Achievement(
    slug=AchievementType.FIRST_ADD_FAVORITE.value,
    name="Premier favori (WIP)",
    description="Ajoute une offre à tes favoris",
    category="Favorites",
    icon="Profile",
)

SECOND_ADD_FAVORITE = Achievement(
    slug=AchievementType.SECOND_ADD_FAVORITE.value,
    name="Second favori (WIP)",
    description="Ajoute une offre à tes favoris",
    category="Favorites",
    icon="Profile",
)

THIRD_ADD_FAVORITE = Achievement(
    slug=AchievementType.THIRD_ADD_FAVORITE.value,
    name="Troisième favori (WIP)",
    description="Ajoute une offre à tes favoris",
    category="Favorites",
    icon="Info",
)

FIRST_WATCH_MOVIE = Achievement(
    slug="FIRST_WATCH_MOVIE",
    name="Premier film (WIP)",
    description="Regarde un film",
    category="Cinema",
    icon="Info",
)

SECOND_WATCH_MOVIE = Achievement(
    slug="SECOND_WATCH_MOVIE",
    name="Second film (WIP)",
    description="Regarde un film",
    category="Cinema",
    icon="Info",
)

THIRD_WATCH_MOVIE = Achievement(
    slug="THIRD_WATCH_MOVIE",
    name="Troisième film (WIP)",
    description="Regarde un film",
    category="Cinema",
    icon="Profile",
)

current_achievements = [
    FIRST_ADD_FAVORITE,
    SECOND_ADD_FAVORITE,
    THIRD_ADD_FAVORITE,
    FIRST_WATCH_MOVIE,
    SECOND_WATCH_MOVIE,
    THIRD_WATCH_MOVIE,
]
