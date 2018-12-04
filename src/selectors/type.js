import createCachedSelector from 're-reselect'

import typesSelector from './types'

function mapArgsToCachedKey(state, isVirtual, offerType) {
  return `${isVirtual || ''}${offerType || ''}`
}

export const typeSelector = createCachedSelector(
  typesSelector,
  (state, isVirtual, offerTypeValue) => offerTypeValue,
  (types, offerTypeValue) =>
    offerTypeValue && types.find(t => t.value === offerTypeValue)
)(mapArgsToCachedKey)
