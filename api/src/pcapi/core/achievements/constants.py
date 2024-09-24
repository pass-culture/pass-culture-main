# {
#     id: 'FIRST_ADD_FAVORITE',
#     name: 'First favorite',
#     description: 'Add your first favorite',
#     category: 'Favorites',
#     icon: 'Profile',
#   },
#   {
#     id: 'SECOND_ADD_FAVORITE',
#     name: 'Second favorite',
#     description: 'Add your second favorite',
#     category: 'Favorites',
#     icon: 'Profile',
#   },
#   {
#     id: 'THIRD_ADD_FAVORITE',
#     name: 'Third favorite',
#     description: 'Add your third favorite',
#     category: 'Favorites',
#     icon: 'Info',
#   },
#   {
#     id: 'FIRST_WATCH_MOVIE',
#     name: 'First movie',
#     description: 'Watch your first movie',
#     category: 'Cinema',
#     icon: 'Info',
#   },
#   {
#     id: 'SECOND_WATCH_MOVIE',
#     name: 'Second movie',
#     description: 'Watch your second movie',
#     category: 'Cinema',
#     icon: 'Info',
#   },
#   {
#     id: 'THIRD_WATCH_MOVIE',
#     name: 'Third movie',
#     description: 'Watch your third movie',
#     category: 'Cinema',
#     icon: 'Profile',
#   },
from pcapi.core.achievements.models import Achievement


FIRST_ADD_FAVORITE = Achievement(
    slug="FIRST_ADD_FAVORITE",
    name="Premier favori (WIP)",
    description="Ajoute une offre à tes favoris",
    category="Favorites",
    icon="Profile",
)

SECOND_ADD_FAVORITE = Achievement(
    slug="SECOND_ADD_FAVORITE",
    name="Second favori (WIP)",
    description="Ajoute une offre à tes favoris",
    category="Favorites",
    icon="Profile",
)

THIRD_ADD_FAVORITE = Achievement(
    slug="THIRD_ADD_FAVORITE",
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
