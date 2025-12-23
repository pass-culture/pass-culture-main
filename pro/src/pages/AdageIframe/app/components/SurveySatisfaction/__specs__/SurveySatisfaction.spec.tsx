import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { apiAdage } from '@/apiClient/api'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { SurveySatisfaction } from '../SurveySatisfaction'

vi.mock('@/apiClient/api', () => ({
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

    const closeButton = screen.getByRole('button', {
      name: 'J’ai déjà répondu',
    })

    await userEvent.click(closeButton)

    await waitFor(() => {
      expect(
        screen.queryByText('Enquête de satisfaction')
      ).not.toBeInTheDocument()
    })
  })

  it('should fail close survey satisfaction', async () => {
    const snackBarError = vi.fn()

    const snackBarsImport = (await vi.importActual(
      '@/commons/hooks/useSnackBar'
    )) as ReturnType<typeof useSnackBar.useSnackBar>
    vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
      ...snackBarsImport,
      error: snackBarError,
    }))

    vi.spyOn(apiAdage, 'saveRedactorPreferences').mockRejectedValue({
      isOk: false,
    })

    renderWithProviders(<SurveySatisfaction {...defaultProps} />)

    screen.getByText('Enquête de satisfaction')

    const closeButton = screen.getByRole('button', {
      name: 'J’ai déjà répondu',
    })

    await userEvent.click(closeButton)

    await waitFor(() => expect(snackBarError).toHaveBeenCalledTimes(1))
  })

  it('should log info when opening sastisfaction survey', async () => {
    renderWithProviders(<SurveySatisfaction {...defaultProps} />)

    const openButton = screen.getByRole('link', {
      name: /Je donne mon avis/,
    })

    await userEvent.click(openButton)

    expect(apiAdage.logOpenSatisfactionSurvey).toHaveBeenCalledWith({
      iframeFrom: '/',
      queryId: '123',
    })
  })
})
