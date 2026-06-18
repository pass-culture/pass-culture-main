import { ActivityNotOpenToPublic } from '@/apiClient/v1'

import { createMap } from '.'
import { putKeyAtTheEnd, sortEntriesByValue } from './helpers'

export const ActivityNotOpenToPublicMap = createMap(
  {
    ARTISTIC_COMPANY: 'Compagnie artistique',
    ARTISTIC_PRACTICE: 'Pratique ou enseignement artistique',
    CULTURAL_MEDIATION: 'Médiation culturelle',
    FESTIVAL: 'Festival',
    HERITAGE_SITE: 'Activité patrimoniale, historique ou touristique',
    HIGHER_EDUCATION_INSTITUTION:
      'Enseignement supérieur (arts, architecture, etc…)',
    MUNICIPALITY_CULTURAL_DEPARTMENT: 'Service culturel de collectivité',
    OTHER: 'Autre',
    PRESS_OR_MEDIA: 'Presse ou média',
    PRODUCTION_OR_PROMOTION_COMPANY: 'Société de production, tourneur ou label',
    PUBLISHING_HOUSE: 'Maison d’édition',
    RADIO_OR_MUSIC_STREAMING: 'Radio ou streaming musical',
    SCIENTIFIC_CULTURE: 'Culture scientifique',
    TELEVISION_OR_VIDEO_STREAMING: 'Télévision ou streaming vidéo',
    TRAVELLING_CINEMA: 'Cinéma itinérant',
  },
  ActivityNotOpenToPublic,
  'ActivityNotOpenToPublic',
  [sortEntriesByValue('fr-FR'), putKeyAtTheEnd('OTHER')]
)
