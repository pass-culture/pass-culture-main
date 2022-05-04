import { render } from '@testing-library/react'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Router } from 'react-router-dom'

import OfferEducationalStock, {
  IOfferEducationalStockProps,
} from '../OfferEducationalStock'

export const renderOfferEducationalStock = (
  props: IOfferEducationalStockProps
) => {
  const history = createBrowserHistory()
  return render(
    <Router history={history}>
      <OfferEducationalStock {...props} />
    </Router>
  )
}
