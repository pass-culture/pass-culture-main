import { render } from '@testing-library/react'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Router } from 'react-router'

import OfferEducationalStock, {
  IOfferEducationalStockProps,
} from '../OfferEducationalStock'

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
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
