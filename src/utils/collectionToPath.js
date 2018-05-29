export default collectionName => {
  switch(collectionName) {
    case 'events':
      return 'evenements'
    case 'objects':
      return 'objets';
    case 'venues':
      return 'lieux';
    default:
      return '';
  }
}