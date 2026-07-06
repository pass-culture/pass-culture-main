import { DisplayableActivity } from '@/apiClient/v1'

import { createMap } from '.'

export const DisplayableActivityMap = createMap(
  {
    ART_GALLERY: 'Galerie d’art',
    ARTISTIC_COMPANY: 'Compagnie artistique',
    ARTISTIC_PRACTICE: 'Pratique ou enseignement artistique',
    ARTS_CENTRE: 'Centre d’arts ou FRAC',
    BOOKSTORE: 'Librairie',
    CINEMA: 'Cinéma',
    COMMUNITY_CENTRE: 'Centre socio-culturel',
    CREATIVE_ARTS_STORE: 'Magasin d’arts créatifs',
    CULTURAL_CENTRE:
      'Lieu culturel pluridisciplinaire (tiers-lieu, friche, etc…)',
    CULTURAL_MEDIATION: 'Médiation culturelle',
    DISTRIBUTION_STORE: 'Magasin de distribution de produits culturels',
    FESTIVAL: 'Festival',
    GAMES_CENTRE: 'Espace ludique',
    HERITAGE_SITE: 'Activité patrimoniale, historique ou touristique',
    HIGHER_EDUCATION_INSTITUTION:
      'Enseignement supérieur (arts, architecture, etc…)',
    LIBRARY: 'Bibliothèque ou médiathèque',
    MUNICIPALITY_CULTURAL_DEPARTMENT: 'Service culturel de collectivité',
    MUSEUM: 'Musée',
    MUSIC_INSTRUMENT_STORE: 'Magasin d’instruments de musique',
    OTHER: 'Autre',
    PERFORMANCE_HALL: 'Salle de spectacles',
    PRESS_OR_MEDIA: 'Presse ou média',
    PRODUCTION_OR_PROMOTION_COMPANY: 'Société de production, tourneur ou label',
    PUBLISHING_HOUSE: 'Maison d’édition',
    RADIO_OR_MUSIC_STREAMING: 'Radio ou streaming musical',
    RECORD_STORE: 'Disquaire',
    SCIENTIFIC_CULTURE: 'Culture scientifique',
    TELEVISION_OR_VIDEO_STREAMING: 'Télévision ou streaming vidéo',
    TOURIST_INFORMATION_CENTRE: 'Office de tourisme',
    TRAVELLING_CINEMA: 'Cinéma itinérant',
  },
  DisplayableActivity,
  'DisplayableActivity'
)
