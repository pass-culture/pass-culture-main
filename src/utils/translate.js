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
