import OfferEducational, { IOfferEducationalProps } from '../OfferEducational'

import { Provider } from 'react-redux'
import React from 'react'
import { Router } from 'react-router-dom'
import { configureTestStore } from 'store/testUtils'
import { createBrowserHistory } from 'history'
import { render } from '@testing-library/react'

export const renderEACOfferForm = (
  props: IOfferEducationalProps,
  store: any = {}
) => {
  const history = createBrowserHistory()
  return render(
    <Provider store={configureTestStore(store)}>
      <Router history={history}>
        <OfferEducational {...props} />
      </Router>
    </Provider>
  )
}
