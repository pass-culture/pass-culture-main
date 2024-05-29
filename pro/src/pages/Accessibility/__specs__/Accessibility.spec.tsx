import { screen } from '@testing-library/react'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import { Accessibility } from '../Accessibility'

describe('Statement of Accessibility page', () => {
  it('should display Accessibility information message', () => {
    renderWithProviders(<Accessibility />)
    expect(screen.getByText('Informations d’accessibilité')).toBeInTheDocument()
  })
})
