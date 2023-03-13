import { screen } from '@testing-library/react'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import Logo from '../Logo'

const renderLogo = props => {
  return renderWithProviders(<Logo {...props} />)
}

describe('header logo', () => {
  it('should link to /accueil when user is not admin', () => {
    // When
    renderLogo({ isUserAdmin: false })

    // Then
    expect(screen.getByRole('link')).toHaveAttribute('href', '/accueil')
  })

  it('should link to /structures when user is admin', () => {
    // When
    renderLogo({ isUserAdmin: true })

    // Then
    expect(screen.getByRole('link')).toHaveAttribute('href', '/structures')
  })
})
