export const GEOLOCATION_CRITERIA = {
  EVERYWHERE: { label: 'Partout', icon: 'ico-globe', requiresGeolocation: false },
  AROUND_ME: { label: 'Autour de moi', icon: 'ico-aroundme', requiresGeolocation: true },
}

export const CATEGORY_CRITERIA = {
  ALL: { label: 'Toutes les catégories', icon: 'ico-gem-stone', filters: [] },
  CINEMA: {
    label: 'Cinéma',
    icon: 'ico-popcorn',
    filters: ['Cinéma', "Carte d'abonnement cinéma"],
  },
  EXHIBITION: {
    label: 'Visites, expositions',
    icon: 'ico-star-struck',
    filters: ['Musée, arts visuels et patrimoine'],
  },
  MUSIC: {
    label: 'Musique',
    icon: 'ico-headphone',
    filters: ['Concert ou festival', 'Abonnements concerts', 'Musique'],
  },
  SHOW: {
    label: 'Spectacles',
    icon: 'ico-studio-microphone',
    filters: ['Spectacle', 'Abonnement spectacles'],
  },
  LESSON: {
    label: 'Cours, ateliers',
    icon: 'ico-performing-arts',
    filters: ['Pratique artistique'],
  },
  BOOK: {
    label: 'Livres',
    icon: 'ico-books',
    filters: ['Livre audio numérique', 'Livre ou carte lecture'],
  },
  FILM: { label: 'Films, séries, podcasts', icon: 'ico-film-frames', filters: ['Film'] },
  PRESS: { label: 'Presse', icon: 'ico-newspaper', filters: ['Presse en ligne'] },
  VIDEO_GAME: {
    label: 'Jeux vidéos',
    icon: 'ico-video-game',
    filters: [
      'Jeux - événement, rencontre ou concours',
      'Jeux - abonnements',
      'Jeu vidéo en ligne',
      'Support physique',
    ],
  },
  CONFERENCE: {
    label: 'Conférences, rencontres',
    icon: 'ico-busts-in-silhouette',
    filters: ['Conférences, rencontres et découverte des métiers'],
  },
  INSTRUMENT: {
    label: 'Instruments de musique',
    icon: 'ico-drum',
    filters: ['Instrument de musique'],
  },
}
