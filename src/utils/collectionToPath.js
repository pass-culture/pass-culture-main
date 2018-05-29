export default collectionName => {
  switch(collectionName) {
    case 'events':
      return 'evenements'
    case 'things':
      return 'objets';
    case 'venues':
      return 'lieux';
    default:
      return '';
  }
}
