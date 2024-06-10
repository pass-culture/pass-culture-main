import { screen } from '@testing-library/react'

import { renderWithProviders } from 'utils/renderWithProviders'

import { MultiyearScheme } from '../MultiyearScheme'

describe('Statement of MultiyearScheme page', () => {
  it('should display MultiyearScheme information message', () => {
    renderWithProviders(<MultiyearScheme />)
    expect(
      screen.getByText('Schéma pluriannuel d’accessibilité 2024 - 2025')
    ).toBeInTheDocument()
  })
})
