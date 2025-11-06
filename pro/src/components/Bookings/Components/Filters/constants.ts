import type { BookingOmniSearchFilters } from './types'

export const ALL_BOOKING_STATUS = []
export const DEFAULT_OMNISEARCH_CRITERIA = 'offre'
export const EMPTY_FILTER_VALUE = ''

type OmnisearchFilter = {
  value: string
  placeholderText: string
  stateKey: keyof BookingOmniSearchFilters
  label: string
}

const offerOmnisearchFilter: OmnisearchFilter = {
  value: 'offre',
  placeholderText: 'Rechercher par nom d’offre',
  stateKey: 'offerName',
  label: 'Offre',
}

const beneficiaryOmnisearchFilter: OmnisearchFilter = {
  value: 'bénéficiaire',
  placeholderText: 'Rechercher par nom ou email',
  stateKey: 'bookingBeneficiary',
  label: 'Bénéficiaire',
}

const eanOmnisearchFilter: OmnisearchFilter = {
  value: 'ean',
  placeholderText: 'Rechercher par EAN-13',
  stateKey: 'offerISBN',
  label: 'EAN-13',
}

const tokenOmnisearchFilter: OmnisearchFilter = {
  value: 'contremarque',
  placeholderText: 'Rechercher par contremarque',
  stateKey: 'bookingToken',
  label: 'Contremarque',
}

export const bookingIdOmnisearchFilter: OmnisearchFilter = {
  value: 'booking_id',
  placeholderText: 'Rechercher par numéro de réservation',
  stateKey: 'bookingId',
  label: 'Numéro de réservation',
}

export const INDIVIDUAL_OMNISEARCH_FILTERS: OmnisearchFilter[] = [
  offerOmnisearchFilter,
  beneficiaryOmnisearchFilter,
  eanOmnisearchFilter,
  tokenOmnisearchFilter,
]
