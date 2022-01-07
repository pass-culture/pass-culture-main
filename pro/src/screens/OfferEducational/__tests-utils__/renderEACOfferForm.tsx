import { render } from '@testing-library/react'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Router } from 'react-router'

import OfferEducational, { IOfferEducationalProps } from '../OfferEducational'

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export const renderEACOfferForm = (props: IOfferEducationalProps) => {
  const history = createBrowserHistory()
  return render(
    <Router history={history}>
      <OfferEducational {...props} />
    </Router>
  )
}
