import { render } from '@testing-library/react'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router-dom'
import type { Store } from 'redux'

import { RootState } from 'store/reducers'
import { configureTestStore } from 'store/testUtils'

import OfferEducationalStock, {
  IOfferEducationalStockProps,
} from '../OfferEducationalStock'

export const renderOfferEducationalStock = (
  props: IOfferEducationalStockProps,
  store: Store<RootState> = configureTestStore({})
) => {
  const history = createBrowserHistory()
  return render(
    <Provider store={store}>
      <Router history={history}>
        <OfferEducationalStock {...props} />
      </Router>
    </Provider>
  )
}
