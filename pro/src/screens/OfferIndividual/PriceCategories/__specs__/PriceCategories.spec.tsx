import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { configureTestStore } from 'store/testUtils'
import { individualOfferFactory } from 'utils/individualApiFactories'

import { PRICE_CATEGORY_MAX_LENGTH } from '../form/constants'
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

  it('should not let add more than 20 price categories', async () => {
    renderPriceCategories({ offer: individualOfferFactory() })

    for (let i = 0; i < PRICE_CATEGORY_MAX_LENGTH - 1; i++) {
      await userEvent.click(screen.getByText('Ajouter un tarif'))
    }

    expect(screen.getByText('Ajouter un tarif')).toBeDisabled()
  })
})
