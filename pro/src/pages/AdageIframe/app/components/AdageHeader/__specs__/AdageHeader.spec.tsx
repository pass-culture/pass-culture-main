import { screen } from '@testing-library/react'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import AdageHeader from '../AdageHeader'

const renderAdageHeader = () => {
  renderWithProviders(<AdageHeader />)
}

describe('AdageHeader', () => {
  it('should render adage header', () => {
    renderAdageHeader()

    expect(screen.getByRole('link', { name: 'Rechercher' })).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Pour mon établissement' })
    ).toBeInTheDocument()
    expect(screen.getByText('Suivi')).toBeInTheDocument()
  })
})
