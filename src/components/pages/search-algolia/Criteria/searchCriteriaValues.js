export const GEOLOCATION_CRITERIA = {
  EVERYWHERE: { label: 'Partout', icon: 'ico-globe', requiresGeolocation: false },
  AROUND_ME: { label: 'Autour de moi', icon: 'ico-aroundme', requiresGeolocation: true },
}

export const CATEGORY_CRITERIA = {
  FILM: { label: 'Films, séries, podcasts', icon: '', filters: ['Film'] },
  CINEMA: { label: 'Cinéma', icon: '', filters: ['Cinéma', "Carte d'abonnement cinéma"] },
  CONFERENCE: {
    label: 'Conférences, rencontres',
    icon: '',
    filters: ['Conférences, rencontres et découverte des métiers'],
  },
  VIDEO_GAME: {
    label: 'Jeux vidéos',
    filters: [
      'Jeux - événement, rencontre ou concours',
      'Jeux - abonnements',
      'Jeu vidéo en ligne',
    ],
  },
  BOOK: { label: 'Livres', icon: '', filters: ['Livre audio numérique', 'Livre ou carte lecture'] },
  EXHIBITION: {
    label: 'Visites, expositions',
    icon: '',
    filters: ['Musée, arts visuels et patrimoine'],
  },
  MUSIC: {
    label: 'Musique',
    icon: '',
    filters: ['Concert ou festival', 'Abonnements concerts', 'Musique'],
  },
  LESSON: { label: 'Cours, ateliers', icon: '', filters: ['Pratique artistique'] },
  PRESS: { label: 'Presse', icon: '', filters: ['Presse en ligne'] },
  SHOW: { label: 'Spectacles', icon: '', filters: ['Spectacle', 'Abonnement spectacles'] },
  INSTRUMENT: { label: 'Instruments de musique', icon: '', filters: ['Instrument de musique'] },
}
