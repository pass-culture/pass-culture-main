import { screen } from '@testing-library/react'
import React from 'react'

import { individualStockFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import StockThingSection from '../StockThingSection'

describe('StockThingSection', () => {
  it('should render correctly', () => {
    const stock = individualStockFactory()

    renderWithProviders(<StockThingSection stock={stock} />)

    expect(screen.queryAllByText(/Prix/)).toHaveLength(1)
  })

  it('should not render if there are no stocks', () => {
    const stock = undefined

    renderWithProviders(<StockThingSection stock={stock} />)

    expect(screen.queryByText(/Prix/)).not.toBeInTheDocument()
  })
})
