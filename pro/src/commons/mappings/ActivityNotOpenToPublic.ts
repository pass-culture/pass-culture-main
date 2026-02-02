export const _ActivityNotOpenToPublicMappings = {
  ARTISTIC_COMPANY: 'Compagnie artistique',
  ARTS_EDUCATION: 'Formation ou enseignement artistique',
  CULTURAL_MEDIATION: 'Médiation culturelle',
  FESTIVAL: 'Festival',
  OTHER: 'Autre',
  PRESS_OR_MEDIA: 'Presse ou média',
  PRODUCTION_OR_PROMOTION_COMPANY: 'Société de production, tourneur ou label',
  RADIO_OR_MUSIC_STREAMING: 'Radio ou streaming musical',
  TELEVISION_OR_VIDEO_STREAMING: 'Télévision ou streaming vidéo',
  TRAVELLING_CINEMA: 'Cinéma itinérant',
}

export type ActivityNotOpenToPublicType =
  keyof typeof _ActivityNotOpenToPublicMappings
