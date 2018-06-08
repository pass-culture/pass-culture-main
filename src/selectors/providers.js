import { createSelector } from 'reselect'

import { getElementsWithoutDeletedFormValues } from '../utils/form'

export default createSelector(
  (state, ownProps) => ownProps.venueProviders,
  state => state.form.providersById,
  (providers, formProvidersById) => {

    // by default it is directly the props providers
    let filteredProviders = providers

    if (formProvidersById) {
      filteredProviders = getElementsWithoutDeletedFormValues(
        providers,
        Object.values(formProvidersById)
      )
    }

    // sort
    if (filteredProviders) {}

    // return
    return filteredProviders
  }
)
