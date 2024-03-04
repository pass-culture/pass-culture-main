import { screen } from '@testing-library/react'
import React from 'react'

import { getIndividualOfferFactory } from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { PriceCategoriesSection } from '../PriceCategoriesSection'

describe('StockEventSection', () => {
  it('should render correctly', () => {
    const offer = getIndividualOfferFactory()

    renderWithProviders(<PriceCategoriesSection offer={offer} canBeDuo />)

    expect(screen.getByText(/Tarifs/)).toBeInTheDocument()
    expect(
      screen.getByText(/Accepter les réservations "Duo"/)
    ).toBeInTheDocument()
  })

  it('should render correctly when offer cannot be duo', () => {
    const offer = getIndividualOfferFactory()

    renderWithProviders(
      <PriceCategoriesSection offer={offer} canBeDuo={false} />
    )

    expect(screen.getByText(/Tarifs/)).toBeInTheDocument()
    expect(
      screen.queryByText(/Accepter les réservations "Duo"/)
    ).not.toBeInTheDocument()
  })
})
