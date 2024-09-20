import { screen, waitFor } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import * as useNotification from 'hooks/useNotification'
import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
  getOffererNameFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { OffererStats } from './OffererStats'

vi.mock('apiClient/api', () => ({
  api: {
    getOfferer: vi.fn(),
    getOffererStatsDashboardUrl: vi.fn(),
    getVenueStatsDashboardUrl: vi.fn(),
    listOfferersNames: vi.fn(),
  },
}))

vi.mock('@firebase/remote-config', () => ({
  getValue: () => ({ asString: () => 'A1' }),
}))

const renderOffererStats = async () => {
  const user = sharedCurrentUserFactory()
  renderWithProviders(<OffererStats />, {
    user,
    storeOverrides: {
      user: {
        currentUser: user,
        selectedOffererId: 1,
      },
    },
  })

  expect(await screen.findByText('Statistiques')).toBeInTheDocument()
}

describe('OffererStatsScreen', () => {
  const firstVenueId = 1
  const secondVenueId = 2
  beforeEach(() => {
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      managedVenues: [
        {
          ...defaultGetOffererVenueResponseModel,
          name: 'Salle 1',
          id: firstVenueId,
        },
        {
          ...defaultGetOffererVenueResponseModel,
          name: 'Stand popcorn',
          id: secondVenueId,
        },
      ],
    })
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [getOffererNameFactory()],
    })
    vi.spyOn(api, 'getOffererStatsDashboardUrl').mockResolvedValue({
      dashboardUrl: 'fakeUrl',
    })
    vi.spyOn(api, 'getVenueStatsDashboardUrl').mockResolvedValue({
      dashboardUrl: 'fakeUrl',
    })
  })

  it('should not display all offerer options on render', async () => {
    await renderOffererStats()
    const offererOption = screen.queryByLabelText('Structure')
    expect(offererOption).not.toBeInTheDocument()
  })

  it('should not display error message if offererNames call fails', async () => {
    vi.spyOn(api, 'listOfferersNames').mockRejectedValue({})

    const notifyError = vi.fn()

    const notifsImport = (await vi.importActual(
      'hooks/useNotification'
    )) as ReturnType<typeof useNotification.useNotification>
    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      ...notifsImport,
      error: notifyError,
    }))
    await renderOffererStats()

    await waitFor(() => {
      expect(api.listOfferersNames).toHaveBeenCalledTimes(1)
    })
    await waitFor(() => expect(notifyError).not.toHaveBeenCalled())
  })
})
