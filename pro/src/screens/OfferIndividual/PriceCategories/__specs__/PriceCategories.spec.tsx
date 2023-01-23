import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { configureTestStore } from 'store/testUtils'
import { individualOfferFactory } from 'utils/individualApiFactories'

import PriceCategories, { IPriceCategories } from '../PriceCategories'

const renderPriceCategories = (props: IPriceCategories) => {
  const store = configureTestStore()

  return render(
    <Provider store={store}>
      <MemoryRouter>
        <PriceCategories {...props} />
      </MemoryRouter>
    </Provider>
  )
}

describe('PriceCategories', () => {
  it('should render without error', () => {
    renderPriceCategories({ offer: individualOfferFactory() })

    screen.getByText('Tarifs')
  })
})
