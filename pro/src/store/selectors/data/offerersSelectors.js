import createCachedSelector from 're-reselect'

export const selectOfferers = state => state.data.offerers

export const selectOffererById = createCachedSelector(
  selectOfferers,
  (state, offererId) => offererId,
  (offerers, offererId) => offerers.find(offerer => offerer.id === offererId)
)((state, offererId = '') => offererId)
