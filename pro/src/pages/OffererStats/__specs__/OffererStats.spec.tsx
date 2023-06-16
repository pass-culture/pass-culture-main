import { screen, waitFor } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import { GetOffererResponseModel } from 'apiClient/v1'
import * as useNotification from 'hooks/useNotification'
import { renderWithProviders } from 'utils/renderWithProviders'

import OffererStats from '../OffererStats'

jest.mock('apiClient/api', () => ({
  api: {
    getOfferer: jest.fn(),
    getOffererStatsDashboardUrl: jest.fn(),
    getVenueStatsDashboardUrl: jest.fn(),
    listOfferersNames: jest.fn(),
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
        nonHumanizedId: '1',
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
    jest.spyOn(api, 'getOfferer').mockResolvedValue({
      managedVenues: [
        { id: 'V1', name: 'Salle 1', nonHumanizedId: firstVenueId },
        { id: 'V2', name: 'Stand popcorn', nonHumanizedId: secondVenueId },
      ],
    } as GetOffererResponseModel)
    jest.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [
        {
          nonHumanizedId: 1,
          name: 'Mon super cinéma',
        },
        {
          nonHumanizedId: 2,
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
    const notifyError = jest.fn()
    // @ts-expect-error
    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
      error: notifyError,
    }))
    jest.spyOn(api, 'listOfferersNames').mockRejectedValueOnce('')
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
