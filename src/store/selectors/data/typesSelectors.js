import { createSelector } from 'reselect'

const selectTypes = state => state.data.types

export const selectTypesByIsVenueVirtual = createSelector(
  selectTypes,
  (state, isVenueVirtual) => isVenueVirtual,
  (types, isVenueVirtual) => {
    let filteredTypes = [ ...types ]
    if (typeof isVenueVirtual !== 'undefined') {
      if (isVenueVirtual) {
        filteredTypes = filteredTypes.filter(type => !type.offlineOnly)
      } else {
        filteredTypes = filteredTypes.filter(type => !type.onlineOnly)
      }
    }
    filteredTypes.sort((t1, t2) => t1.proLabel.localeCompare(t2.proLabel))
    return filteredTypes
  }
)

export const selectTypeValueByOffer = createSelector(
  selectTypes,
  (state, offer) => offer,
  (types, offer) => {
    const { type: offerType } = offer
    if (offerType.includes('ACTIVATION')) {
      return 'Pass Culture : activation'
    }
    return types.find(type => type.value === offerType).proLabel
  }
)
