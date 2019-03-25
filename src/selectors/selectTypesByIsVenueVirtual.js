import { createSelector } from 'reselect'

export const selectTypesByIsVenueVirtual = createSelector(
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
    filteredTypes.sort((t1, t2) => t1.label.localeCompare(t2.label))
    return filteredTypes
  }
)

export default selectTypesByIsVenueVirtual
