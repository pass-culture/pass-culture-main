import invert from 'lodash.invert'

import { OfferStatus } from 'apiClient/v1'

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
  active: OfferStatus.ACTIVE,
  inactive: OfferStatus.INACTIVE,
  epuisee: OfferStatus.SOLD_OUT,
  expiree: OfferStatus.EXPIRED,
  'en-attente': OfferStatus.PENDING,
  refusee: OfferStatus.REJECTED,
  draft: OfferStatus.DRAFT,
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
