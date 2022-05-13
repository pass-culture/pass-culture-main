import OfferEducational, { IOfferEducationalProps } from '../OfferEducational'

import React from 'react'
import { Router } from 'react-router-dom'
import { createBrowserHistory } from 'history'
import { render } from '@testing-library/react'

export const renderEACOfferForm = (props: IOfferEducationalProps) => {
  const history = createBrowserHistory()
  return render(
    <Router history={history}>
      <OfferEducational {...props} />
    </Router>
  )
}
