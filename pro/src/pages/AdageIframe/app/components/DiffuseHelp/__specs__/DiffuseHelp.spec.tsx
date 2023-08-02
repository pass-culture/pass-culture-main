import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import { DiffuseHelp } from '../DiffuseHelp'

describe('DiffuseHelp', () => {
  it('should close diffuse help', async () => {
    renderWithProviders(<DiffuseHelp description="test 123" />)

    screen.getByText('Le saviez-vous ?')

    const closeButton = screen.getByTestId('close-diffuse-help')

    userEvent.click(closeButton)

    await waitFor(() => {
      expect(screen.queryByText('Le saviez-vous ?')).not.toBeInTheDocument()
    })
  })
})
