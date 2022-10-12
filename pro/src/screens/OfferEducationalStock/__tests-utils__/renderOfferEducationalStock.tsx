import { render } from '@testing-library/react'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router-dom'

import { configureTestStore } from 'store/testUtils'

import OfferEducationalStock, {
  IOfferEducationalStockProps,
} from '../OfferEducationalStock'

export const renderOfferEducationalStock = (
  props: IOfferEducationalStockProps
) => {
  const history = createBrowserHistory()
  return render(
    <Provider store={configureTestStore({})}>
      <Router history={history}>
        <OfferEducationalStock {...props} />
      </Router>
    </Provider>
  )
}
