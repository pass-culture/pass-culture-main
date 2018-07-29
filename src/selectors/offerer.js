import createCachedSelector from 're-reselect'

import offerersSelector from './offerers'

export default createCachedSelector(
  state => offerersSelector(state),
  (state, offererId) => offererId,
  (offerers, offererId) => offerers.find(offerer => offerer.id === offererId)
)((state, offererId) => offererId || '')
