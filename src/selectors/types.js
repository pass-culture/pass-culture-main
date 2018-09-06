import { createSelector } from 'reselect'

export default createSelector(
  state => state.data.types,
  (state, isVenueVirtual) => isVenueVirtual,
  (types, isVenueVirtual) => {
    let filteredTypes = types.map(t => {
      const [, value] = t.value.split('.')
      return Object.assign({}, t, { value })
    })
    if (typeof isVenueVirtual !== 'undefined') {
      if (isVenueVirtual) {
        filteredTypes = filteredTypes.filter(t => !t.offlineOnly)
      } else {
        filteredTypes = filteredTypes.filter(t => !t.onlineOnly)
      }
    }
    filteredTypes.sort((t1, t2) => t1.label.localeCompare(t2.label))
    return filteredTypes
  }
)
