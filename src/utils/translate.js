export function collectionToPath (collectionName) {
  switch(collectionName) {
    case 'events':
      return 'evenements'
    case 'mediations':
      return 'accroches'
    case 'venues':
      return 'lieux';
    case 'offerers':
      return 'etablissements'
    case 'things':
      return 'objets'
    default:
      return collectionName
  }
}

export function pathToCollection (path) {
  switch(path) {
    case 'accroches':
      return 'mediations'
    case 'evenements':
      return 'events'
    case 'lieux':
      return 'venues'
    case 'objets':
      return 'things';
    case 'etablissements':
      return 'offerers'
    default:
      return path;
  }
}

export function pathToModel (path) {
  switch(path) {
    case 'accroches':
      return 'mediation'
    case 'evenements':
      return 'event'
    case 'lieux':
      return 'venue'
    case 'objets':
      return 'thing';
    case 'etablissements':
      return 'offerer'
    default:
      return path;
  }
}
