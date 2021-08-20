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
    facetFilter: 'Cinéma',
  },
  EXHIBITION: {
    label: 'Visites, expositions',
    icon: 'ico-exposition',
    facetFilter: 'Visites, expositions',
  },
  MUSIC: {
    label: 'Musique',
    icon: 'ico-music',
    facetFilter: 'Musique',
  },
  SHOW: {
    label: 'Spectacles',
    icon: 'ico-show',
    facetFilter: 'Spectacles',
  },
  LESSON: {
    label: 'Cours, ateliers',
    icon: 'ico-arts',
    facetFilter: 'Cours, ateliers',
  },
  BOOK: {
    label: 'Livres',
    icon: 'ico-books',
    facetFilter: 'Livres',
  },
  FILM: {
    label: 'Films, séries, podcasts',
    icon: 'ico-movie',
    facetFilter: 'Films, séries, podcasts',
  },
  PRESS: {
    label: 'Presse',
    icon: 'ico-newspaper',
    facetFilter: 'Presse',
  },
  GAME: {
    label: 'Jeux',
    icon: 'ico-game',
    facetFilter: 'Jeux',
  },
  CONFERENCE: {
    label: 'Conférences, rencontres',
    icon: 'ico-conference',
    facetFilter: 'Conférences, rencontres',
  },
  INSTRUMENT: {
    label: 'Instruments de musique',
    icon: 'ico-instrument',
    facetFilter: 'Instruments de musique',
  },
  ART_SUPPLY: {
    label: 'Matériel arts créatifs',
    icon: 'ico-materiel-creatif',
    facetFilter: 'Matériel arts créatifs',
  },
}
