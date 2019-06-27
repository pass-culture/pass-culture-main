import { createSelector } from 'reselect'

const selectCurrentPathnameFeature = createSelector(
  state => state.data.features,
  (state, pathname) => pathname,
  (features, pathname) =>
    (features || []).find(feature => feature.pathname === pathname)
)

export default selectCurrentPathnameFeature
