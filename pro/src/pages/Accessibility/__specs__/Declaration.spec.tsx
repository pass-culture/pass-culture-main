import { screen } from '@testing-library/react'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import { Declaration } from '../Declaration'

describe('Statement of Declaration page', () => {
  it('should display Declaration information message', () => {
    renderWithProviders(<Declaration />)
    expect(screen.getByText(/Déclaration d’accessibilité/)).toBeInTheDocument()
  })
})
