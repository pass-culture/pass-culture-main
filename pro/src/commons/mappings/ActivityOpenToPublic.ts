import { ActivityOpenToPublic } from '@/apiClient/v1/new'

import { createMap } from '.'
import { putKeyAtTheEnd, sortEntriesByValue } from './helpers'

export const ActivityOpenToPublicMap = createMap(
  {
    ART_GALLERY: 'Galerie d’art',
    ARTISTIC_PRACTICE: 'Pratique ou enseignement artistique',
    ARTS_CENTRE: 'Centre d’arts ou FRAC',
    BOOKSTORE: 'Librairie',
    CINEMA: 'Cinéma',
    COMMUNITY_CENTRE: 'Centre socio-culturel',
    CREATIVE_ARTS_STORE: 'Magasin d’arts créatifs',
    CULTURAL_CENTRE:
      'Lieu culturel pluridisciplinaire (tiers-lieu, friche, etc…)',
    DISTRIBUTION_STORE: 'Magasin de distribution de produits culturels',
    FESTIVAL: 'Festival',
    HERITAGE_SITE: 'Activité patrimoniale, historique ou touristique',
    HIGHER_EDUCATION_INSTITUTION:
      'Enseignement supérieur (arts, architecture, etc…)',
    LIBRARY: 'Bibliothèque ou médiathèque',
    MUSEUM: 'Musée',
    MUSIC_INSTRUMENT_STORE: 'Magasin d’instruments de musique',
    OTHER: 'Autre',
    PERFORMANCE_HALL: 'Salle de spectacles',
    PUBLISHING_HOUSE: 'Maison d’édition',
    RECORD_STORE: 'Disquaire',
    SCIENTIFIC_CULTURE: 'Culture scientifique',
    TOURIST_INFORMATION_CENTRE: 'Office de tourisme',
  },
  ActivityOpenToPublic,
  'ActivityOpenToPublic',
  [sortEntriesByValue('fr-FR'), putKeyAtTheEnd('OTHER')]
)
