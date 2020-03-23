export const GEOLOCATION_CRITERIA = {
  EVERYWHERE: { label: 'Partout', icon: 'ico-globe', requiresGeolocation: false },
  AROUND_ME: { label: 'Autour de moi', icon: 'ico-aroundme', requiresGeolocation: true },
}

export const CATEGORY_CRITERIA = {
  ALL: { label: 'Toutes les catégories', icon: 'ico-gem-stone', filters: [], facetFilter: '' },
  CINEMA: {
    label: 'Cinéma',
    icon: 'ico-popcorn',
    filters: ['Cinéma', "Carte d'abonnement cinéma"],
    facetFilter: 'CINEMA',
  },
  EXHIBITION: {
    label: 'Visites, expositions',
    icon: 'ico-star-struck',
    filters: ['Musée, arts visuels et patrimoine'],
    facetFilter: 'VISITE',
  },
  MUSIC: {
    label: 'Musique',
    icon: 'ico-headphone',
    filters: ['Concert ou festival', 'Abonnements concerts', 'Musique'],
    facetFilter: 'MUSIQUE',
  },
  SHOW: {
    label: 'Spectacles',
    icon: 'ico-studio-microphone',
    filters: ['Spectacle', 'Abonnement spectacles'],
    facetFilter: 'SPECTACLE',
  },
  LESSON: {
    label: 'Cours, ateliers',
    icon: 'ico-performing-arts',
    filters: ['Pratique artistique'],
    facetFilter: 'LECON',
  },
  BOOK: {
    label: 'Livres',
    icon: 'ico-books',
    filters: ['Livre audio numérique', 'Livre ou carte lecture'],
    facetFilter: 'LIVRE',
  },
  FILM: {
    label: 'Films, séries, podcasts',
    icon: 'ico-film-frames',
    filters: ['Film'],
    facetFilter: 'FILM',
  },
  PRESS: {
    label: 'Presse',
    icon: 'ico-newspaper',
    filters: ['Presse en ligne'],
    facetFilter: 'PRESSE',
  },
  VIDEO_GAME: {
    label: 'Jeux vidéos',
    icon: 'ico-video-game',
    filters: [
      'Jeux - événement, rencontre ou concours',
      'Jeux - abonnements',
      'Jeu vidéo en ligne',
      'Support physique',
    ],
    facetFilter: 'JEUX_VIDEO',
  },
  CONFERENCE: {
    label: 'Conférences, rencontres',
    icon: 'ico-busts-in-silhouette',
    filters: ['Conférences, rencontres et découverte des métiers'],
    facetFilter: 'CONFERENCE',
  },
  INSTRUMENT: {
    label: 'Instruments de musique',
    icon: 'ico-drum',
    filters: ['Instrument de musique'],
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
