export const _ActivityNotOpenToPublicMappings = {
  ARTISTIC_COMPANY: 'Compagnie artistique',
  ARTS_EDUCATION: 'Formation ou enseignement artistique',
  CULTURAL_MEDIATION: 'Médiation culturelle',
  FESTIVAL: 'Festival',
  OTHER: 'Autre',
  PRESS: 'Presse',
  PRODUCTION_OR_PROMOTION_COMPANY: 'Société de production, tourneur ou label',
  STREAMING_PLATFORM: 'Plateforme de streaming musique ou vidéo',
  TRAVELLING_CINEMA: 'Cinéma itinérant',
}

export type ActivityNotOpenToPublicType =
  keyof typeof _ActivityNotOpenToPublicMappings
