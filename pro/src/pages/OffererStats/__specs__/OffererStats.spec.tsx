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

import { OffererStats } from '../OffererStats'

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

const renderOffererStats = () => {
  renderWithProviders(<OffererStats />, { user: sharedCurrentUserFactory() })
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
      offerersNames: [
        getOffererNameFactory({
          id: 1,
          name: 'Mon super cinéma',
        }),
        getOffererNameFactory({
          id: 2,
          name: 'Ma super librairie',
        }),
      ],
    })
    vi.spyOn(api, 'getOffererStatsDashboardUrl').mockResolvedValue({
      dashboardUrl: 'fakeUrl',
    })
    vi.spyOn(api, 'getVenueStatsDashboardUrl').mockResolvedValue({
      dashboardUrl: 'fakeUrl',
    })
  })

  it('should display all offerer options on render', async () => {
    renderOffererStats()

    await waitFor(() => {
      expect(api.listOfferersNames).toHaveBeenCalledTimes(1)
    })
    const offererOption = await screen.findByText('Mon super cinéma')
    expect(offererOption).toBeInTheDocument()
  })

  it('should display error message if api call fail', async () => {
    const notifyError = vi.fn()

    const notifsImport = (await vi.importActual(
      'hooks/useNotification'
    )) as ReturnType<typeof useNotification.useNotification>
    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      ...notifsImport,
      error: notifyError,
    }))
    vi.spyOn(api, 'listOfferersNames').mockRejectedValueOnce('')
    renderOffererStats()

    await waitFor(() => {
      expect(api.listOfferersNames).toHaveBeenCalledTimes(1)
    })
    await waitFor(() =>
      expect(notifyError).toHaveBeenNthCalledWith(
        1,
        'Nous avons rencontré un problème lors de la récupération des données.'
      )
    )
  })
})
