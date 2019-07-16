import createCachedSelector from 're-reselect'

import selectTypesByIsVenueVirtual from './selectTypesByIsVenueVirtual'

function mapArgsToCachedKey(state, isVirtual, offerType) {
  return `${isVirtual || ''}${offerType || ''}`
}

const selectTypeByIsVenueVirtualAndOfferTypeValue = createCachedSelector(
  selectTypesByIsVenueVirtual,
  (state, isVirtual, offerTypeValue) => offerTypeValue,
  (types, offerTypeValue) => offerTypeValue && types.find(t => t.value === offerTypeValue)
)(mapArgsToCachedKey)

export default selectTypeByIsVenueVirtualAndOfferTypeValue
