import { createSelector } from 'reselect'

import selectOfferers from './offerers'

export default createSelector(
  selectOfferers,
  offerers => {
    const offererOptions = offerers && [{
      label: 'Sélectionnez une structure',
    }].concat(offerers.map(o => ({ label: o.name, value: o.id })))
    if (offererOptions && offererOptions.length === 2) {
      return [offererOptions[1]]
    }
    return offererOptions
  }
)
