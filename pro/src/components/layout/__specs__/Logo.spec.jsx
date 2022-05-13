import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'

import Logo from '../Logo'
import { MemoryRouter } from 'react-router'
import React from 'react'

const renderLogo = props => {
  return render(
    <MemoryRouter>
      <Logo {...props} />
    </MemoryRouter>
  )
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
