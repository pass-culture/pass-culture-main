import { render } from '@testing-library/react'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Router } from 'react-router-dom'

import OfferEducational, { IOfferEducationalProps } from '../OfferEducational'

export const renderEACOfferForm = (props: IOfferEducationalProps) => {
  const history = createBrowserHistory()
  return render(
    <Router history={history}>
      <OfferEducational {...props} />
    </Router>
  )
}
