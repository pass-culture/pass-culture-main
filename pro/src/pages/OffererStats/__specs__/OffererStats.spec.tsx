import { screen, waitFor } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import { GetOffererResponseModel } from 'apiClient/v1'
import * as useNotification from 'hooks/useNotification'
import { renderWithProviders } from 'utils/renderWithProviders'

import OffererStats from '../OffererStats'

vi.mock('apiClient/api', () => ({
  api: {
    getOfferer: vi.fn(),
    getOffererStatsDashboardUrl: vi.fn(),
    getVenueStatsDashboardUrl: vi.fn(),
    listOfferersNames: vi.fn(),
  },
}))

jest.mock('@firebase/remote-config', () => ({
  getValue: () => ({ asString: () => 'A1' }),
}))

jest.mock('hooks/useRemoteConfig', () => ({
  __esModule: true,
  default: () => ({ remoteConfig: {} }),
}))

const renderOffererStats = () => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        firstName: 'John',
        dateCreated: '2022-07-29T12:18:43.087097Z',
        email: 'john@do.net',
        id: '1',
        isAdmin: false,
        isEmailValidated: true,
        roles: [],
      },
    },
  }

  renderWithProviders(<OffererStats />, { storeOverrides })
}

describe('OffererStatsScreen', () => {
  const firstVenueId = 1
  const secondVenueId = 2
  beforeEach(() => {
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      managedVenues: [
        { name: 'Salle 1', id: firstVenueId },
        { name: 'Stand popcorn', id: secondVenueId },
      ],
    } as GetOffererResponseModel)
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [
        {
          id: 1,
          name: 'Mon super cinéma',
        },
        {
          id: 2,
          name: 'Ma super librairie',
        },
      ],
    })
    jest
      .spyOn(api, 'getOffererStatsDashboardUrl')
      .mockResolvedValue({ dashboardUrl: 'fakeUrl' })
    jest
      .spyOn(api, 'getVenueStatsDashboardUrl')
      .mockResolvedValue({ dashboardUrl: 'fakeUrl' })
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
    // @ts-expect-error
    vi.spyOn(useNotification, 'default').mockImplementation(() => ({
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
