import { screen } from '@testing-library/react'
import React from 'react'

import {
  individualOfferFactory,
  individualStockFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import StockThingSection from '../StockThingSection'

describe('StockThingSection', () => {
  it('should render correctly', () => {
    const offer = individualOfferFactory({
      isEvent: false,
      stocks: [individualStockFactory()],
    })

    renderWithProviders(<StockThingSection offer={offer} />)

    expect(screen.queryAllByText(/Prix/)).toHaveLength(1)
  })

  it('should not render if there are no stocks', () => {
    const offer = individualOfferFactory({ stocks: [] })

    renderWithProviders(<StockThingSection offer={offer} />)

    expect(screen.queryByText(/Prix/)).not.toBeInTheDocument()
  })

  it('should render duo informations', () => {
    const offer = individualOfferFactory({
      isEvent: false,
      stocks: [individualStockFactory()],
    })

    renderWithProviders(<StockThingSection offer={offer} canBeDuo={true} />)

    expect(
      screen.getByText(/Accepter les réservations "Duo"/)
    ).toBeInTheDocument()
  })
})
