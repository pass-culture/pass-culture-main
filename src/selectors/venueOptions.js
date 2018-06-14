import { createSelector } from 'reselect'

import selectSelectedVenues from './selectedVenues'

export default createSelector(
  selectSelectedVenues,
  venues => {
    const venueOptions = venues && [{
      label: 'Sélectionnez un lieu',
    }].concat(venues).map(v =>
      ({ label: v.name, value: v.id }))
    if (venueOptions && venueOptions.length === 2) {
      return [venueOptions[1]]
    }
    return venueOptions
  }
)
