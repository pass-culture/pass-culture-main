import { screen } from '@testing-library/react'
import React from 'react'

import { individualOfferFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import PriceCategories, { IPriceCategories } from '../PriceCategories'

const renderPriceCategories = (props: IPriceCategories) =>
  renderWithProviders(<PriceCategories {...props} />)

describe('PriceCategories', () => {
  it('should render without error', () => {
    renderPriceCategories({ offer: individualOfferFactory() })

    expect(screen.getByText('Tarifs')).toBeInTheDocument()
    expect(screen.getByText('Réservations “Duo”')).toBeInTheDocument()
  })

  // TODO not implemented yet: Test submit logic
})
