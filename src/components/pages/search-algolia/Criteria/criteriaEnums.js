export const GEOLOCATION_CRITERIA = {
  EVERYWHERE: { label: 'Partout', icon: 'ico-globe', requiresGeolocation: false },
  AROUND_ME: { label: 'Autour de moi', icon: 'ico-aroundme', requiresGeolocation: true },
}

export const CATEGORY_CRITERIA = {
  ALL: { label: 'Toutes les catégories', icon: 'ico-gem-stone', facetFilter: '' },
  CINEMA: {
    label: 'Cinéma',
    icon: 'ico-popcorn',
    facetFilter: 'CINEMA',
  },
  EXHIBITION: {
    label: 'Visites, expositions',
    icon: 'ico-star-struck',
    facetFilter: 'VISITE',
  },
  MUSIC: {
    label: 'Musique',
    icon: 'ico-headphone',
    facetFilter: 'MUSIQUE',
  },
  SHOW: {
    label: 'Spectacles',
    icon: 'ico-studio-microphone',
    facetFilter: 'SPECTACLE',
  },
  LESSON: {
    label: 'Cours, ateliers',
    icon: 'ico-performing-arts',
    facetFilter: 'LECON',
  },
  BOOK: {
    label: 'Livres',
    icon: 'ico-books',
    facetFilter: 'LIVRE',
  },
  FILM: {
    label: 'Films, séries, podcasts',
    icon: 'ico-film-frames',
    facetFilter: 'FILM',
  },
  PRESS: {
    label: 'Presse',
    icon: 'ico-newspaper',
    facetFilter: 'PRESSE',
  },
  VIDEO_GAME: {
    label: 'Jeux vidéos',
    icon: 'ico-video-game',
    facetFilter: 'JEUX_VIDEO',
  },
  CONFERENCE: {
    label: 'Conférences, rencontres',
    icon: 'ico-busts-in-silhouette',
    facetFilter: 'CONFERENCE',
  },
  INSTRUMENT: {
    label: 'Instruments de musique',
    icon: 'ico-drum',
    facetFilter: 'INSTRUMENT',
  },
}

export const SORT_CRITERIA = {
  RANDOM: {
    label: 'Au hasard',
    icon: 'ico-random',
    index: '',
    requiresGeolocation: false,
  },
  NEAR_ME: {
    label: 'Proximité',
    icon: 'ico-nearme',
    index: '_by_proximity',
    requiresGeolocation: true,
  },
  NEW: {
    label: 'Nouveauté',
    icon: 'ico-new',
    index: '_by_novelty',
    requiresGeolocation: false,
  },
  PRICE: {
    label: 'Prix',
    icon: 'ico-price',
    index: '_by_price',
    requiresGeolocation: false,
  },
}
