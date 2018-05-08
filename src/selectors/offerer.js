import { createSelector } from 'reselect'

export default createSelector(
  (state, ownProps) => ownProps.match.params.offererId,
  state => state.user,
  (offererId, user) =>
    user && user.offerers.find(o => o.id === offererId)
)
