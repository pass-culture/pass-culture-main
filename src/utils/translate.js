export function collectionToPath (collectionName) {
  switch(collectionName) {
    case 'events':
      return 'evenements'
    case 'things':
      return 'objets';
    case 'venues':
      return 'etablissements';
    default:
      return collectionName;
  }
}

export function pathToCollection (path) {
  switch(path) {
    case 'evenements':
      return 'events'
    case 'objets':
      return 'things';
    case 'etablissements':
      return 'venues';
    default:
      return path;
  }
}
