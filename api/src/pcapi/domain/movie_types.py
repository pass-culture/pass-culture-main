from dataclasses import dataclass


@dataclass
class MovieType:
    label: str
    name: str
    children: list | None = None


movie_types = [
    MovieType(name="ACTION", label="Action"),
    MovieType(name="ADVENTURE", label="Aventure"),
    MovieType(name="ANIMATION", label="Animation"),
    MovieType(name="BIOPIC", label="Biopic"),
    MovieType(name="BOLLYWOOD", label="Bollywood"),
    MovieType(name="COMEDY", label="Comédie"),
    MovieType(name="COMEDY_DRAMA", label="Comédie dramatique"),
    MovieType(name="CONCERT", label="Concert"),
    MovieType(name="DETECTIVE", label="Policier"),
    MovieType(name="DIVERS", label="Divers"),
    MovieType(name="DOCUMENTARY", label="Documentaire"),
    MovieType(name="DRAMA", label="Drame"),
    MovieType(name="EROTIC", label="Érotique"),
    MovieType(name="EXPERIMENTAL", label="Expérimental"),
    MovieType(name="FAMILY", label="Familial"),
    MovieType(name="FANTASY", label="Fantastique"),
    MovieType(name="HISTORICAL", label="Historique"),
    MovieType(name="HISTORICAL_EPIC", label="Historique-épique"),
    MovieType(name="HORROR", label="Horreur"),
    MovieType(name="JUDICIAL", label="Judiciaire"),
    MovieType(name="KOREAN_DRAMA", label="Drame coréen"),
    MovieType(name="MARTIAL_ARTS", label="Arts martiaux"),
    MovieType(name="MUSIC", label="Musique"),
    MovieType(name="MUSICAL", label="Comédie musicale"),
    MovieType(name="OPERA", label="Opéra"),
    MovieType(name="PERFORMANCE", label="Performance"),
    MovieType(name="ROMANCE", label="Romance"),
    MovieType(name="SCIENCE_FICTION", label="Science-fiction"),
    MovieType(name="SPORT_EVENT", label="Sport"),
    MovieType(name="SPY", label="Espionnage"),
    MovieType(name="THRILLER", label="Thriller"),
    MovieType(name="WARMOVIE", label="Guerre"),
    MovieType(name="WESTERN", label="Western"),
]
