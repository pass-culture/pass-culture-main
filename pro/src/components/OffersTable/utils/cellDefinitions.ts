export type CellDefinition = {
  id: string
  title: string
}

type CELLS =
  | 'CHECKBOX'
  | 'INFO_ON_EXPIRATION'
  | 'THUMB'
  | 'NAME'
  | 'EVENT_DATE'
  | 'VENUE'
  | 'ADDRESS'
  | 'STRUCTURE'
  | 'INSTITUTION'
  | 'STOCKS'
  | 'COLLECTIVE_STATUS'
  | 'INDIVIDUAL_STATUS'
  | 'ACTIONS'

export function getCellsDefinition(
  isRefactoFutureOfferEnabled: boolean = false
): Record<CELLS, CellDefinition> {
  return {
    CHECKBOX: {
      id: 'offer-head-checkbox',
      title: '',
    },
    INFO_ON_EXPIRATION: {
      id: 'offer-head-info-on-expiration',
      title: 'Information sur l’expiration',
    },
    THUMB: {
      id: 'offer-head-image',
      title: 'Image',
    },
    NAME: {
      id: 'offer-head-name',
      title: 'Nom de l’offre',
    },
    EVENT_DATE: {
      id: 'offer-head-event-date',
      title: 'Date de l’évènement',
    },
    VENUE: {
      id: 'offer-head-venue',
      title: 'Lieu',
    },
    ADDRESS: {
      id: 'offer-head-address',
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
    STOCKS: {
      id: 'offer-head-stocks',
      title: 'Stocks',
    },
    COLLECTIVE_STATUS: {
      id: 'offer-head-status',
      title: 'Statut',
    },
    INDIVIDUAL_STATUS: {
      id: 'offer-head-status',
      title: isRefactoFutureOfferEnabled ? 'Publication' : 'Statut',
    },
    ACTIONS: {
      id: 'offer-head-actions',
      title: 'Actions',
    },
  }
}
