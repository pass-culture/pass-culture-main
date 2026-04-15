export const _ActivityOpenToPublicMappings = {
  ART_GALLERY: 'Galerie d’art',
  ART_SCHOOL: 'Conservatoire ou école d’arts',
  ARTISTIC_PRACTICE: 'Pratique ou enseignement artistique',
  ARTS_CENTRE: 'Centre d’arts',
  BOOKSTORE: 'Librairie',
  CINEMA: 'Cinéma',
  COMMUNITY_CENTRE: 'Centre socio-culturel',
  CREATIVE_ARTS_STORE: 'Magasin d’arts créatifs',
  CULTURAL_CENTRE: 'Centre culturel pluridisciplinaire',
  DISTRIBUTION_STORE: 'Magasin de distribution de produits culturels',
  FESTIVAL: 'Festival',
  HERITAGE_SITE: 'Activité patrimoniale, historique ou touristique',
  LIBRARY: 'Bibliothèque ou médiathèque',
  MUSEUM: 'Musée',
  MUSIC_INSTRUMENT_STORE: 'Magasin d’instruments de musique',
  OTHER: 'Autre',
  PERFORMANCE_HALL: 'Salle de spectacles',
  PUBLISHING_HOUSE: 'Maison d’édition',
  RECORD_STORE: 'Disquaire',
  SCIENCE_CENTRE: 'Centre de culture scientifique, technique et industrielle',
  TOURIST_INFORMATION_CENTRE: 'Office de tourisme',
}

export type ActivityOpenToPublicType =
  keyof typeof _ActivityOpenToPublicMappings
