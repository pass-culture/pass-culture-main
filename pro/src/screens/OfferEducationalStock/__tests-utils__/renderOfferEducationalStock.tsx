import OfferEducationalStock, {
  IOfferEducationalStockProps,
} from '../OfferEducationalStock'

import React from 'react'
import { Router } from 'react-router-dom'
import { createBrowserHistory } from 'history'
import { render } from '@testing-library/react'

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
