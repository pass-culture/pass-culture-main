import get from 'lodash.get'
import createCachedSelector from 're-reselect'

import selectActiveMediationsByOfferId from './selectActiveMediationsByOfferId'
import selectProductById from './selectProductById'
import { THUMBS_URL } from '../utils/config'

function mapArgsToCacheKey(state, offerId, productId) {
  return `${offerId || ''}/${productId || ''}`
}

export const selectThumbUrlByOfferIdAndProductId = createCachedSelector(
  (state, offerId, productId) =>
    selectActiveMediationsByOfferId(state, offerId),
  (state, offerId, productId) => selectProductById(state, productId),
  (mediations, product) => {
    if (get(mediations, '0')) {
      return `${THUMBS_URL}/mediations/${mediations[0].id}`
    }

    if (get(product, 'thumbCount')) {
      return `${THUMBS_URL}/products/${get(product, 'id')}`
    }

    return (
      get(product, 'thumbCount') &&
      `${THUMBS_URL}/products/${get(product, 'id')}`
    )
  }
)(mapArgsToCacheKey)

export default selectThumbUrlByOfferIdAndProductId
