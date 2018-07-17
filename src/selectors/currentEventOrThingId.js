import { createSelector } from 'reselect'

export default createSelector(
  state => state.router.location.hash,
  hash => hash.substr(1)
)
