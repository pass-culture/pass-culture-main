import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import * as localStorageAvailable from 'utils/localStorageAvailable'
import { renderWithProviders } from 'utils/renderWithProviders'

import { DiffuseHelp } from '../DiffuseHelp'

describe('DiffuseHelp', () => {
  it('should close diffuse help', async () => {
    renderWithProviders(<DiffuseHelp description="test 123" />)

    screen.getByText('Le saviez-vous ?')

    const closeButton = screen.getByTestId('close-diffuse-help')

    await userEvent.click(closeButton)

    await waitFor(() => {
      expect(screen.queryByText('Le saviez-vous ?')).not.toBeInTheDocument()
    })
  })

  it('should not display disffuse help if the localstorage is not available', () => {
    vi.spyOn(
      localStorageAvailable,
      'localStorageAvailable'
    ).mockImplementationOnce(() => false)

    renderWithProviders(<DiffuseHelp description="test 123" />)

    expect(screen.queryByText('Le saviez-vous ?')).not.toBeInTheDocument()
  })
})
