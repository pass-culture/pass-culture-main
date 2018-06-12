import { createSelector } from 'reselect'

import { getElementsWithoutDeletedFormValues } from '../utils/form'

export default createSelector(
  (state, ownProps) => ownProps.venueProviders,
  state => state.form.venueProvidersById,
  (venueProviders, formVenueProvidersById) => {

    // by default it is directly the props providers
    let filteredVenueProviders = venueProviders

    if (venueProviders && formVenueProvidersById) {
      filteredVenueProviders = getElementsWithoutDeletedFormValues(
        venueProviders,
        Object.values(formVenueProvidersById)
      )
    }

    // sort
    if (filteredVenueProviders) {}

    // return
    return filteredVenueProviders
  }
)
