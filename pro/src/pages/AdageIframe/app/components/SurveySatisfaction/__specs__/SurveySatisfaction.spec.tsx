import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { apiAdage } from 'apiClient/api'
import * as useNotification from 'hooks/useNotification'
import { renderWithProviders } from 'utils/renderWithProviders'

import { SurveySatisfaction } from '../SurveySatisfaction'

vi.mock('apiClient/api', () => ({
  apiAdage: {
    saveRedactorPreferences: jest.fn(() => Promise.resolve({})),
  },
}))

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

  it('should fail close survey satisfaction', async () => {
    const notifyError = vi.fn()
    // @ts-expect-error
    vi.spyOn(useNotification, 'default').mockImplementation(() => ({
      error: notifyError,
    }))

    vi.spyOn(apiAdage, 'saveRedactorPreferences').mockRejectedValue({
      isOk: false,
    })

    renderWithProviders(<SurveySatisfaction />)

    screen.getByText('Enquête de satisfaction')

    const closeButton = screen.getByTitle('Masquer le bandeau')

    userEvent.click(closeButton)

    await waitFor(() => expect(notifyError).toHaveBeenCalledTimes(1))
  })
})
