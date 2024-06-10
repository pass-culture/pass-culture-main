import { screen } from '@testing-library/react'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import { Commitment } from '../Commitment'

describe('Statement of Commitment page', () => {
  it('should display Commitment information message', () => {
    renderWithProviders(<Commitment />)
    expect(
      screen.getByText(
        'Les engagements du pass Culture pour l’accessibilité numérique'
      )
    ).toBeInTheDocument()
  })
})
