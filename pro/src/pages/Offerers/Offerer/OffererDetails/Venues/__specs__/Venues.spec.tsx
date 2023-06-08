import { screen } from '@testing-library/react'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import Venues from '../Venues'

describe('Venues', () => {
  const offererId = 1

  const renderReturnVenues = (storeOverrides = {}) =>
    renderWithProviders(<Venues offererId={1} venues={[]} />, {
      storeOverrides,
    })

  it('should render a title', () => {
    renderReturnVenues({
      features: {
        list: [{ isActive: true, nameKey: 'API_SIRENE_AVAILABLE' }],
      },
    })

    expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent('Lieux')
  })

  it('should render a create venue link when the venue creation is available', () => {
    renderReturnVenues({
      features: {
        list: [{ isActive: true, nameKey: 'API_SIRENE_AVAILABLE' }],
      },
    })

    expect(screen.getAllByRole('link')[0]).toHaveAttribute(
      'href',
      `/structures/${offererId}/lieux/creation`
    )
  })

  it('should render a create venue link when the venue creation is disabled', () => {
    renderReturnVenues()

    expect(screen.getAllByRole('link')[0]).toHaveAttribute(
      'href',
      '/erreur/indisponible'
    )
  })
})
