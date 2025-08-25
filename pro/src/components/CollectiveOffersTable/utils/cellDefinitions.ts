export type CellDefinition = {
  id: string
  title: string
}

type CELLS =
  | 'CHECKBOX'
  | 'INFO_ON_EXPIRATION'
  | 'NAME'
  | 'EVENT_DATE'
  | 'VENUE'
  | 'LOCATION'
  | 'STRUCTURE'
  | 'INSTITUTION'
  | 'COLLECTIVE_STATUS'
  | 'ACTIONS'
  | 'PRICE_AND_PARTICIPANTS'

export function getCellsDefinition(): Record<CELLS, CellDefinition> {
  return {
    CHECKBOX: {
      id: 'offer-head-checkbox',
      title: '',
    },
    INFO_ON_EXPIRATION: {
      id: 'offer-head-info-on-expiration',
      title: 'Information sur l’expiration',
    },
    NAME: {
      id: 'offer-head-name',
      title: 'Nom de l’offre',
    },
    EVENT_DATE: {
      id: 'offer-head-event-date',
      title: 'Dates',
    },
    VENUE: {
      id: 'offer-head-venue',
      title: 'Lieu',
    },
    LOCATION: {
      id: 'offer-head-location',
      title: 'Localisation',
    },
    STRUCTURE: {
      id: 'offer-head-structure',
      title: 'Structure',
    },
    INSTITUTION: {
      id: 'offer-head-institution',
      title: 'Établissement',
    },
    COLLECTIVE_STATUS: {
      id: 'offer-head-status',
      title: 'Statut',
    },
    ACTIONS: {
      id: 'offer-head-actions',
      title: 'Actions',
    },
    PRICE_AND_PARTICIPANTS: {
      id: 'offer-head-price-and-participants',
      title: 'Prix et participants',
    },
  }
}
