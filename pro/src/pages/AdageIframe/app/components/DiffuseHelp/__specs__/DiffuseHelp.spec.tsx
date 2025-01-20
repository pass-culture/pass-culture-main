import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { renderWithProviders } from 'commons/utils/renderWithProviders'
import * as storageAvailable from 'commons/utils/storageAvailable'

import { DiffuseHelp } from '../HighlightBanner'

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
      storageAvailable,
      'storageAvailable'
    ).mockImplementationOnce(() => false)

    renderWithProviders(<DiffuseHelp description="test 123" />)

    expect(screen.queryByText('Le saviez-vous ?')).not.toBeInTheDocument()
  })
})
