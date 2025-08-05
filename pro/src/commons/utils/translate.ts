import { CollectiveOfferDisplayedStatus, OfferStatus } from 'apiClient/v1'
import { SearchFiltersParams } from 'commons/core/Offers/types'
import { Audience } from 'commons/core/shared/types'
import invert from 'lodash/invert'

const translateObjectKeysAndValues = (
  originalObject: Record<string, any>,
  translationsMap: Record<string, string>
) => {
  const nonTranlatedKeys = ['nom-ou-isbn', 'nameOrIsbn'] //  These keys should not have their values translated since it's user inputs

  const result: Record<string, string> = {}
  Object.entries(originalObject).forEach(([originalKey, originalValue]) => {
    const translatedKey = translationsMap[originalKey] ?? originalKey

    const translatedValue =
      Object.keys(translationsMap).includes(originalValue) &&
      !nonTranlatedKeys.includes(originalKey)
        ? translationsMap[originalValue]
        : originalValue

    result[translatedKey] = Array.isArray(translatedValue)
      ? translatedValue.map((value) => translationsMap[value])
      : translatedValue
  })
  return result
}

const mapBrowserStatusToApi: Record<string, OfferStatus> = {
  active: OfferStatus.ACTIVE,
  inactive: OfferStatus.INACTIVE,
  epuisee: OfferStatus.SOLD_OUT,
  expiree: OfferStatus.EXPIRED,
  'en-attente': OfferStatus.PENDING,
  refusee: OfferStatus.REJECTED,
  draft: OfferStatus.DRAFT,
}

const mapBrowserCollectiveStatusToApi: Record<
  string,
  CollectiveOfferDisplayedStatus
> = {
  active: CollectiveOfferDisplayedStatus.PUBLISHED,
  inactive: CollectiveOfferDisplayedStatus.HIDDEN,
  prereservee: CollectiveOfferDisplayedStatus.PREBOOKED,
  reservee: CollectiveOfferDisplayedStatus.BOOKED,
  expiree: CollectiveOfferDisplayedStatus.EXPIRED,
  terminee: CollectiveOfferDisplayedStatus.ENDED,
  'en-attente': CollectiveOfferDisplayedStatus.UNDER_REVIEW,
  refusee: CollectiveOfferDisplayedStatus.REJECTED,
  archivee: CollectiveOfferDisplayedStatus.ARCHIVED,
  brouillon: CollectiveOfferDisplayedStatus.DRAFT,
  remboursee: CollectiveOfferDisplayedStatus.REIMBURSED,
  annulee: CollectiveOfferDisplayedStatus.CANCELLED,
}

const mapBrowserToApi = (audience: Audience) => ({
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
  ...(audience === Audience.INDIVIDUAL
    ? mapBrowserStatusToApi
    : mapBrowserCollectiveStatusToApi),
})

export const translateQueryParamsToApiParams = (
  queryParams: Record<string, string | string[]>,
  audience: Audience
) => translateObjectKeysAndValues(queryParams, mapBrowserToApi(audience))

export const translateApiParamsToQueryParams = (
  apiParams: Partial<SearchFiltersParams>,
  audience: Audience
) => translateObjectKeysAndValues(apiParams, invert(mapBrowserToApi(audience)))
