import invert from 'lodash.invert'

export function collectionToPath(collectionName) {
  switch (collectionName) {
    case 'events':
      return 'evenements'
    case 'mediations':
      return 'accroches'
    case 'venues':
      return 'lieux'
    case 'offerers':
      return 'structures'
    case 'things':
      return 'objets'
    default:
      return collectionName
  }
}

export function pathToCollection(path) {
  switch (path) {
    case 'accroches':
      return 'mediations'
    case 'evenements':
      return 'events'
    case 'lieux':
      return 'venues'
    case 'objets':
      return 'things'
    case 'structures':
      return 'offerers'
    default:
      return path
  }
}

export function pathToModel(path) {
  switch (path) {
    case 'evenements':
      return 'Event'
    case 'objets':
      return 'Thing'
    default:
      return path
  }
}

export function modelToPath(model) {
  switch (model) {
    case 'Event':
      return 'evenements'
    case 'Thing':
      return 'lieux'
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
  date: 'eventOccurrenceIdOrNew',
  lieu: 'venueId',
  [`mots-cles`]: 'keywords',
  structure: 'offererId',
  stock: 'stockIdOrNew',
}

export const mapApiToBrowser = invert(mapBrowserToApi)

export function translateBrowserUrlToApiUrl(query) {
  return getObjectWithMappedKeys(query, mapBrowserToApi)
}
