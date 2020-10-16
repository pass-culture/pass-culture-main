import merge from 'lodash.merge'

import configureStore from 'store'
import { initialState as bookingSummaryInitialState } from 'store/reducers/bookingSummary/bookingSummary'
import { initialState as dataInitialState } from 'store/reducers/data'
import { initialState as errorsInitialState } from 'store/reducers/errors'
import { initialState as maintenanceInitialState } from 'store/reducers/maintenanceReducer'
import { initialState as modalInitialState } from 'store/reducers/modal'
import { initialState as offersInitialState } from 'store/reducers/offers'

export const configureTestStore = overrideData => {
  const initialData = {
    bookingSummary: bookingSummaryInitialState,
    data: dataInitialState,
    errors: errorsInitialState,
    maintenance: maintenanceInitialState,
    modal: modalInitialState,
    offers: offersInitialState,
  }

  return configureStore(merge(initialData, overrideData)).store
}
