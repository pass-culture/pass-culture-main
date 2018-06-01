import { createSelector } from 'reselect'

export default createSelector(
  state => state.user.offerers,
  (state, ownProps) => ownProps.match.params.offererId,
  (offerers, offererId) => {
    if (!offerers) { return }
    return offerers.find(o => o.id === offererId)
  }
)
