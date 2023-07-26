import invert from 'lodash/invert'

import { OfferStatus } from 'apiClient/v1'
import { CollectiveOfferStatus } from 'core/OfferEducational'
import { SearchFiltersParams } from 'core/Offers/types'

function getObjectWithMappedKeys(obj: any, keysMap: Record<string, string>) {
  const mappedObj: Record<string, string> = {}
  Object.keys(obj).forEach(objKey => {
    let mappedKey = objKey
    if (keysMap[objKey]) {
      mappedKey = keysMap[objKey]
    }
    mappedObj[mappedKey] = obj[objKey]
  })
  return mappedObj
}

export const mapBrowserStatusToApi: Record<
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

export const mapBrowserToApi = {
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

export const mapApiToBrowser = invert(mapBrowserToApi)

export function translateQueryParamsToApiParams(
  queryParams: Record<string, string>
) {
  return getObjectWithMappedKeys(queryParams, mapBrowserToApi)
}

export function translateApiParamsToQueryParams(
  apiParams: Partial<SearchFiltersParams>
) {
  return getObjectWithMappedKeys(apiParams, mapApiToBrowser)
}
