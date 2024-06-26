import { BookingOmniSearchFilters } from './types'

export const ALL_BOOKING_STATUS = []
export const DEFAULT_OMNISEARCH_CRITERIA = 'offre'
export const EMPTY_FILTER_VALUE = ''

type OmnisearchFilter = {
  id: string
  placeholderText: string
  stateKey: keyof BookingOmniSearchFilters
  selectOptionText: string
}

const offerOmnisearchFilter: OmnisearchFilter = {
  id: 'offre',
  placeholderText: 'Rechercher par nom d’offre',
  stateKey: 'offerName',
  selectOptionText: 'Offre',
}

const beneficiaryOmnisearchFilter: OmnisearchFilter = {
  id: 'bénéficiaire',
  placeholderText: 'Rechercher par nom ou email',
  stateKey: 'bookingBeneficiary',
  selectOptionText: 'Bénéficiaire',
}

const institutionOmnisearchFilter: OmnisearchFilter = {
  id: 'établissement',
  placeholderText: 'Rechercher par nom d’établissement',
  stateKey: 'bookingInstitution',
  selectOptionText: 'Établissement',
}

const eanOmnisearchFilter: OmnisearchFilter = {
  id: 'ean',
  placeholderText: 'Rechercher par EAN-13',
  stateKey: 'offerISBN',
  selectOptionText: 'EAN-13',
}

const tokenOmnisearchFilter: OmnisearchFilter = {
  id: 'contremarque',
  placeholderText: 'Rechercher par contremarque',
  stateKey: 'bookingToken',
  selectOptionText: 'Contremarque',
}

export const bookingIdOmnisearchFilter: OmnisearchFilter = {
  id: 'booking_id',
  placeholderText: 'Rechercher par numéro de réservation',
  stateKey: 'bookingId',
  selectOptionText: 'Numéro de réservation',
}

export const INDIVIDUAL_OMNISEARCH_FILTERS: OmnisearchFilter[] = [
  offerOmnisearchFilter,
  beneficiaryOmnisearchFilter,
  eanOmnisearchFilter,
  tokenOmnisearchFilter,
]
export const COLLECTIVE_OMNISEARCH_FILTERS: OmnisearchFilter[] = [
  offerOmnisearchFilter,
  institutionOmnisearchFilter,
  bookingIdOmnisearchFilter,
]
