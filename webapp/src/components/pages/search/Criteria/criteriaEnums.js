export const GEOLOCATION_CRITERIA = {
  EVERYWHERE: {
    label: 'Partout',
    icon: 'ico-everywhere',
    requiresGeolocation: false,
  },
  AROUND_ME: {
    label: 'Autour de moi',
    icon: 'ico-around-me',
    requiresGeolocation: true,
  },
}

export const CATEGORY_CRITERIA = {
  ALL: {
    label: 'Toutes les catégories',
    icon: 'ico-all',
    facetFilter: '',
  },
  CINEMA: {
    label: 'Cinéma',
    icon: 'ico-cinema',
    facetFilter: 'CINEMA',
  },
  EXHIBITION: {
    label: 'Visites, expositions',
    icon: 'ico-exposition',
    facetFilter: 'VISITE',
  },
  MUSIC: {
    label: 'Musique',
    icon: 'ico-music',
    facetFilter: 'MUSIQUE',
  },
  SHOW: {
    label: 'Spectacles',
    icon: 'ico-show',
    facetFilter: 'SPECTACLE',
  },
  LESSON: {
    label: 'Cours, ateliers',
    icon: 'ico-arts',
    facetFilter: 'COURS',
  },
  BOOK: {
    label: 'Livres',
    icon: 'ico-books',
    facetFilter: 'LIVRE',
  },
  FILM: {
    label: 'Films, séries, podcasts',
    icon: 'ico-movie',
    facetFilter: 'FILM',
  },
  PRESS: {
    label: 'Presse',
    icon: 'ico-newspaper',
    facetFilter: 'PRESSE',
  },
  GAME: {
    label: 'Jeux',
    icon: 'ico-game',
    facetFilter: 'JEU',
  },
  CONFERENCE: {
    label: 'Conférences, rencontres',
    icon: 'ico-conference',
    facetFilter: 'CONFERENCE',
  },
  INSTRUMENT: {
    label: 'Instruments de musique',
    icon: 'ico-instrument',
    facetFilter: 'INSTRUMENT',
  },
  ART_SUPPLY: {
    label: 'Matériel arts créatifs',
    icon: 'ico-materiel-creatif',
    facetFilter: 'MATERIEL',
  },
}
