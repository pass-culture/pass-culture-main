export function collectionToPath (collectionName) {
  switch(collectionName) {
    case 'events':
      return 'evenements'
    case 'venues':
      return 'lieux';
    case 'things':
      return 'objets';
    case 'venues':
      return 'lieux';
    default:
      return collectionName;
  }
}

export function pathToCollection (path) {
  switch(path) {
    case 'evenements':
      return 'events'
    case 'lieux':
      return 'venues';
    case 'objets':
      return 'things';
    case 'etablissements':
      return 'offerers';
    default:
      return path;
  }
}
