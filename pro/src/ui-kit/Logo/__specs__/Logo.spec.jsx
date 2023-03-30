import { screen } from '@testing-library/react'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import Logo from '../Logo'

const renderLogo = () => {
  return renderWithProviders(<Logo />)
}

describe('header logo', () => {
  it('should link to /accueil', () => {
    // When
    renderLogo()

    // Then
    expect(screen.getByRole('link')).toHaveAttribute('href', '/accueil')
  })
})
