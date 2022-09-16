import { BookingOmniSearchFilters } from './types'

type OmnisearchFilter = {
  id: string
  placeholderText: string
  stateKey: keyof BookingOmniSearchFilters
  selectOptionText: string
}

const offerOmnisearchFilter: OmnisearchFilter = {
  id: 'offre',
  placeholderText: "Rechercher par nom d'offre",
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

const isbnOmnisearchFilter: OmnisearchFilter = {
  id: 'isbn',
  placeholderText: 'Rechercher par ISBN',
  stateKey: 'offerISBN',
  selectOptionText: 'ISBN',
}

const tokenOmnisearchFilter: OmnisearchFilter = {
  id: 'contremarque',
  placeholderText: 'Rechercher par contremarque',
  stateKey: 'bookingToken',
  selectOptionText: 'Contremarque',
}

export const INDIVIDUAL_OMNISEARCH_FILTERS: OmnisearchFilter[] = [
  offerOmnisearchFilter,
  beneficiaryOmnisearchFilter,
  isbnOmnisearchFilter,
  tokenOmnisearchFilter,
]
export const COLLECTIVE_OMNISEARCH_FILTERS: OmnisearchFilter[] = [
  offerOmnisearchFilter,
  institutionOmnisearchFilter,
]
