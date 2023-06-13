import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import { SurveySatisfaction } from '../SurveySatisfaction'

describe('SurveySatisfaction', () => {
  it('should close survey satisfaction', async () => {
    renderWithProviders(<SurveySatisfaction />)

    screen.getByText('Enquête de satisfaction')

    const closeButton = screen.getByTitle('Masquer le bandeau')

    userEvent.click(closeButton)

    await waitFor(() => {
      expect(
        screen.queryByText('Enquête de satisfaction')
      ).not.toBeInTheDocument()
    })
  })
})
