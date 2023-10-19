import { screen } from '@testing-library/react'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import { StatisticsDashboard } from '../StatisticsDashboard'

const renderStatisticsDashboard = () => {
  return renderWithProviders(<StatisticsDashboard offererId="1" />)
}

describe('PriceCategories', () => {
  it('should render without error', () => {
    renderStatisticsDashboard()

    expect(screen.getByText('Présence sur le pass Culture')).toBeInTheDocument()
  })
})
