import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectOfferers from './offerers'

export default createSelector(
  selectOfferers,
  (state, ownProps) => get(ownProps, 'match.params.offererId'),
  (offerers, offererId) => {

    let filteredOfferers = offerers

    if (offererId) {
      filteredOfferers = offerers.find(offerer => offerer.id === offererId)
    }

    return filteredOfferers && filteredOfferers.map(o =>
      ({ label: o.name, value: o.id }))
  }
)
