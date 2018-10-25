import createCachedSelector from 're-reselect'

import offerersSelector from './offerers'

export const selectOffererById = createCachedSelector(
  state => offerersSelector(state),
  (state, offererId) => offererId,
  (offerers, offererId) => offerers.find(offerer => offerer.id === offererId)
)((state, offererId) => offererId || '')

export default selectOffererById
