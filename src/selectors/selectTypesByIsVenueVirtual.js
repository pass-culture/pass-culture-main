import { createSelector } from 'reselect'

const selectTypesByIsVenueVirtual = createSelector(
  state => state.data.types,
  (state, isVenueVirtual) => isVenueVirtual,
  (types, isVenueVirtual) => {
    let filteredTypes = [...types]
    if (typeof isVenueVirtual !== 'undefined') {
      if (isVenueVirtual) {
        filteredTypes = filteredTypes.filter(t => !t.offlineOnly)
      } else {
        filteredTypes = filteredTypes.filter(t => !t.onlineOnly)
      }
    }
    filteredTypes.sort((t1, t2) => t1.proLabel.localeCompare(t2.proLabel))
    return filteredTypes
  }
)

export default selectTypesByIsVenueVirtual
