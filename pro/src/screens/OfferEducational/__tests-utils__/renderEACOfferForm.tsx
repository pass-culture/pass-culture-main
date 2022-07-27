import { render } from '@testing-library/react'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router-dom'

import { configureTestStore } from 'store/testUtils'

import OfferEducational, { IOfferEducationalProps } from '../OfferEducational'

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
