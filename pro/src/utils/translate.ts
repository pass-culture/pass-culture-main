import invert from 'lodash/invert'

import { CollectiveOfferDisplayedStatus, OfferStatus } from 'apiClient/v1'
import { SearchFiltersParams } from 'core/Offers/types'

const translateObjectKeysAndValues = (
  originalObject: Record<string, any>,
  translationsMap: Record<string, string>
) => {
  const result: Record<string, string> = {}
  Object.entries(originalObject).forEach(([originalKey, originalValue]) => {
    const translatedKey = translationsMap[originalKey] ?? originalKey

    const translatedValue = Object.keys(translationsMap).includes(originalValue)
      ? translationsMap[originalValue]
      : originalValue

    result[translatedKey] = translatedValue
  })

  return result
}

// This is a bit janky because for types used by both individual and collective offers,
// we only declare one type here. It works but only because
// the individual and collective types share the same values
// (ie OfferStatus.ACTIVE === CollectiveOfferDisplayedStatus.ACTIVE)
// TODO refactor to split individual and collective behavior
const mapBrowserStatusToApi: Record<
  string,
  OfferStatus | CollectiveOfferDisplayedStatus
> = {
  active: OfferStatus.ACTIVE,
  inactive: OfferStatus.INACTIVE,
  epuisee: OfferStatus.SOLD_OUT,
  prereservee: CollectiveOfferDisplayedStatus.PREBOOKED,
  reservee: CollectiveOfferDisplayedStatus.BOOKED,
  expiree: OfferStatus.EXPIRED,
  terminee: CollectiveOfferDisplayedStatus.ENDED,
  'en-attente': OfferStatus.PENDING,
  refusee: OfferStatus.REJECTED,
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
