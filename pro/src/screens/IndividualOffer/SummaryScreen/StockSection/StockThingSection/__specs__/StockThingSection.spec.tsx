import { screen } from '@testing-library/react'

import { getOfferStockFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { StockThingSection } from '../StockThingSection'

describe('StockThingSection', () => {
  it('should render correctly', () => {
    const stock = getOfferStockFactory()

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

  it('should render duo informations for can be duo things (like ESCAPE_GAME or CARTE_MUSEE)', () => {
    const stock = getOfferStockFactory()

    renderWithProviders(
      <StockThingSection stock={stock} canBeDuo={true} isDuo={true} />
    )

    expect(
      screen.getByText('Accepter les réservations "Duo" :')
    ).toBeInTheDocument()
    expect(screen.getByText('Oui')).toBeInTheDocument()
  })
})
