import createCachedSelector from 're-reselect'

import offersSelector from './offers'

export default createCachedSelector(
  state => offersSelector(state),
  (state, offerId) => offerId,
  (offers, offerId) => offers.find(o => o.id === offerId)
)((state, offerId) => offerId || '')
