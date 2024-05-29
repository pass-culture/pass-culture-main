import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { apiAdage } from 'apiClient/api'
import * as useNotification from 'hooks/useNotification'
import { renderWithProviders } from 'utils/renderWithProviders'

import { SurveySatisfaction } from '../SurveySatisfaction'

vi.mock('apiClient/api', () => ({
  apiAdage: {
    saveRedactorPreferences: vi.fn(),
    logOpenSatisfactionSurvey: vi.fn(),
  },
}))

describe('SurveySatisfaction', () => {
  const defaultProps = {
    queryId: '123',
  }
  it('should close survey satisfaction', async () => {
    renderWithProviders(<SurveySatisfaction {...defaultProps} />)

    screen.getByText('Enquête de satisfaction')

    const closeButton = screen.getByTitle('Masquer le bandeau')

    await userEvent.click(closeButton)

    await waitFor(() => {
      expect(
        screen.queryByText('Enquête de satisfaction')
      ).not.toBeInTheDocument()
    })
  })

  it('should fail close survey satisfaction', async () => {
    const notifyError = vi.fn()

    const notifsImport = (await vi.importActual(
      'hooks/useNotification'
    )) as ReturnType<typeof useNotification.useNotification>
    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      ...notifsImport,
      error: notifyError,
    }))

    vi.spyOn(apiAdage, 'saveRedactorPreferences').mockRejectedValue({
      isOk: false,
    })

    renderWithProviders(<SurveySatisfaction {...defaultProps} />)

    screen.getByText('Enquête de satisfaction')

    const closeButton = screen.getByTitle('Masquer le bandeau')

    await userEvent.click(closeButton)

    await waitFor(() => expect(notifyError).toHaveBeenCalledTimes(1))
  })

  it('should log info when opening sastisfaction survey', async () => {
    renderWithProviders(<SurveySatisfaction {...defaultProps} />)

    const openButton = screen.getByRole('link', {
      name: 'Nouvelle fenêtre Je donne mon avis',
    })

    await userEvent.click(openButton)

    expect(apiAdage.logOpenSatisfactionSurvey).toHaveBeenCalledWith({
      iframeFrom: '/',
      queryId: '123',
    })
  })
})
