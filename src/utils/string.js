// eslint-disable prefer-const
function queryStringToObject(string = '') {
  return string
    .replace(/^\??/, '')
    .split('&')
    .filter(el => el)
    .reduce((result, group) => {
      let [key, value] = group.split('=') // eslint-disable-line
      switch (key) {
        case 'date':
          key = 'eventOccurrenceIdOrNew'
          break
        case 'stock':
          key = 'stockIdOrNew'
          break
        case 'lieu':
          key = 'venueId'
          break
        case 'structure':
          key = 'offererId'
          break
        default:
          break
      }
      return Object.assign({}, result, { [key]: value })
    }, {})
}

export default queryStringToObject
