import createCachedSelector from 're-reselect'

import { selectTypesByIsVenueVirtual } from '../../../../selectors/data/typesSelectors'

const selectTypeByIsVenueVirtualAndOfferTypeValue = createCachedSelector(
  selectTypesByIsVenueVirtual,
  (state, isVirtual, offerTypeValue) => offerTypeValue,
  (types, offerTypeValue) => offerTypeValue && types.find(type => type.value === offerTypeValue)
)((state, isVirtual = '', offerType = '') => `${isVirtual}${offerType}`)

export default selectTypeByIsVenueVirtualAndOfferTypeValue
