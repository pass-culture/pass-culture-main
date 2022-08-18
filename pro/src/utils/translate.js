import invert from 'lodash.invert'

import {
  OFFER_STATUS_ACTIVE,
  OFFER_STATUS_EXPIRED,
  OFFER_STATUS_INACTIVE,
  OFFER_STATUS_PENDING,
  OFFER_STATUS_REJECTED,
  OFFER_STATUS_SOLD_OUT,
} from 'core/Offers'

function getObjectWithMappedKeys(obj, keysMap) {
  const mappedObj = {}
  Object.keys(obj).forEach(objKey => {
    let mappedKey = objKey
    if (keysMap[objKey]) {
      mappedKey = keysMap[objKey]
    }
    mappedObj[mappedKey] = obj[objKey]
  })
  return mappedObj
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
  active: OFFER_STATUS_ACTIVE,
  inactive: OFFER_STATUS_INACTIVE,
  epuisee: OFFER_STATUS_SOLD_OUT,
  expiree: OFFER_STATUS_EXPIRED,
  'en-attente': OFFER_STATUS_PENDING,
  refusee: OFFER_STATUS_REJECTED,
  statut: 'status',
  creation: 'creationMode',
  manuelle: 'manual',
  importee: 'imported',
  'periode-evenement-debut': 'periodBeginningDate',
  'periode-evenement-fin': 'periodEndingDate',
  page: 'page',
  individuel: 'individual',
  collectif: 'collective',
}

export const mapApiToBrowser = invert(mapBrowserToApi)

export function translateQueryParamsToApiParams(queryParams) {
  return getObjectWithMappedKeys(queryParams, mapBrowserToApi)
}

export function translateApiParamsToQueryParams(apiParams) {
  return getObjectWithMappedKeys(apiParams, mapApiToBrowser)
}
