import invert from 'lodash.invert'

import {
  OFFER_STATUS_ACTIVE,
  OFFER_STATUS_EXPIRED,
  OFFER_STATUS_INACTIVE,
  OFFER_STATUS_PENDING,
  OFFER_STATUS_REJECTED,
  OFFER_STATUS_SOLD_OUT,
} from 'core/Offers/constants'

export function collectionToPath(collectionName) {
  switch (collectionName) {
    case 'mediations':
      return 'accroches'
    case 'venues':
      return 'lieux'
    case 'offerers':
      return 'structures'
    case 'products':
      return 'produits'
    default:
      return collectionName
  }
}

export function pathToCollection(path) {
  switch (path) {
    case 'accroches':
      return 'mediations'
    case 'lieux':
      return 'venues'
    case 'produits':
      return 'products'
    case 'structures':
      return 'offerers'
    default:
      return path
  }
}

export function pathToModel(path) {
  switch (path) {
    case 'product':
      return 'Product'
    default:
      return path
  }
}

export function modelToPath(model) {
  switch (model) {
    case 'Product':
      return 'product'
    default:
      return model
  }
}

export function typeToTag(type) {
  switch (type) {
    case 'ComedyEvent':
      return 'Comédie'
    case 'DanceEvent':
      return 'Danse'
    case 'Festival':
      return 'Festival'
    case 'LiteraryEvent':
      return 'Lecture'
    case 'MusicEvent':
      return 'Musique'
    case 'ScreeningEvent':
      return 'Cinéma'
    case 'TheaterEvent':
      return 'Théâtre'
    default:
      return type
  }
}

export function getObjectWithMappedKeys(obj, keysMap) {
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
