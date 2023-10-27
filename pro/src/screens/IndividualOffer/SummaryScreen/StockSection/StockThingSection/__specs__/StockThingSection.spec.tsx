import { screen } from '@testing-library/react'
import React from 'react'

import { individualStockFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import StockThingSection from '../StockThingSection'

describe('StockThingSection', () => {
  it('should render correctly', () => {
    const stock = individualStockFactory()

    renderWithProviders(
      <StockThingSection stock={stock} canBeDuo={false} isDuo={false} />
    )

    expect(screen.getByText(/Prix/)).toBeInTheDocument()
  })

  it('should not render if there are no stocks', () => {
    const stock = undefined

    renderWithProviders(
      <StockThingSection stock={stock} canBeDuo={false} isDuo={false} />
    )

    expect(screen.queryByText(/Prix/)).not.toBeInTheDocument()
  })

  it('should render duo informations for can be duo things (like ESCAPE_GAME, CARTE_MUSEE or ABO_MUSEE)', () => {
    const stock = individualStockFactory()

    renderWithProviders(
      <StockThingSection stock={stock} canBeDuo={true} isDuo={true} />
    )

    expect(
      screen.getByText('Accepter les réservations "Duo" :')
    ).toBeInTheDocument()
    expect(screen.getByText('Oui')).toBeInTheDocument()
  })
})
