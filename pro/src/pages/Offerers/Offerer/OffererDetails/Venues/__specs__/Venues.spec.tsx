import { screen } from '@testing-library/react'
import React from 'react'

import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'

import { Venues } from '../Venues'

describe('Venues', () => {
  const offererId = 1

  const renderReturnVenues = (options?: RenderWithProvidersOptions) =>
    renderWithProviders(<Venues offererId={1} venues={[]} />, options)

  it('should render a title', () => {
    renderReturnVenues({ features: ['API_SIRENE_AVAILABLE'] })

    expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent('Lieux')
  })

  it('should render a create venue link when the venue creation is available', () => {
    renderReturnVenues({ features: ['API_SIRENE_AVAILABLE'] })

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
