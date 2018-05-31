export function collectionToPath (collectionName) {
  switch(collectionName) {
    case 'events':
      return 'evenements'
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
    case 'objets':
      return 'things';
    case 'lieux':
      return 'venues';
    default:
      return path;
  }
}
