import invert from 'lodash/invert'

import { OfferStatus } from 'apiClient/v1'
import { CollectiveOfferStatus } from 'core/OfferEducational'
import { SearchFiltersParams } from 'core/Offers/types'

const translateObjectKeysAndValues = (
  originalObject: Record<string, any>,
  translationsMap: Record<string, string>
) => {
  const result: Record<string, string> = {}
  Object.entries(originalObject).forEach(([originalKey, originalValue]) => {
    const translatedKey = translationsMap[originalKey] ?? originalKey
    const translatedValue = translationsMap[originalValue] ?? originalValue

    result[translatedKey] = translatedValue
  })

  return result
}

const mapBrowserStatusToApi: Record<
  string,
  OfferStatus | CollectiveOfferStatus
> = {
  active: OfferStatus.ACTIVE || CollectiveOfferStatus.ACTIVE,
  inactive: OfferStatus.INACTIVE || CollectiveOfferStatus.INACTIVE,
  epuisee: OfferStatus.SOLD_OUT,
  prereservee: CollectiveOfferStatus.PREBOOKED,
  reservee: CollectiveOfferStatus.BOOKED,
  expiree: OfferStatus.EXPIRED || CollectiveOfferStatus.EXPIRED,
  terminee: CollectiveOfferStatus.ENDED,
  'en-attente': OfferStatus.PENDING || CollectiveOfferStatus.PENDING,
  refusee: OfferStatus.REJECTED || CollectiveOfferStatus.REJECTED,
  draft: OfferStatus.DRAFT,
}

const mapBrowserToApi = {
  categorie: 'categoryId',
  de: 'from',
  lieu: 'venueId',
  'mots-cles': 'keywords',
  nom: 'name',
  'nom-ou-isbn': 'nameOrIsbn',
  remboursements: 'reimbursements',
  reservations: 'bookings',
  structure: 'offererId',
  stock: 'stockIdOrNew',
  statut: 'status',
  creation: 'creationMode',
  manuelle: 'manual',
  importee: 'imported',
  'periode-evenement-debut': 'periodBeginningDate',
  'periode-evenement-fin': 'periodEndingDate',
  page: 'page',
  individuel: 'individual',
  collectif: 'collective',
  ...mapBrowserStatusToApi,
}

const mapApiToBrowser = invert(mapBrowserToApi)

export const translateQueryParamsToApiParams = (
  queryParams: Record<string, string>
) => translateObjectKeysAndValues(queryParams, mapBrowserToApi)

export const translateApiParamsToQueryParams = (
  apiParams: Partial<SearchFiltersParams>
) => translateObjectKeysAndValues(apiParams, mapApiToBrowser)
