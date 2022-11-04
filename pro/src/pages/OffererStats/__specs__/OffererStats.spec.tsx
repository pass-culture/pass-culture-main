import '@testing-library/jest-dom'
import { render, screen, waitFor } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import type { Store } from 'redux'

import { api } from 'apiClient/api'
import { GetOffererResponseModel } from 'apiClient/v1'
import * as useNotification from 'hooks/useNotification'
import { configureTestStore } from 'store/testUtils'

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

const renderOffererStats = (store: Store) => {
  render(
    <Provider store={store}>
      <OffererStats />
    </Provider>
  )
}

describe('OffererStatsScreen', () => {
  let currentUser
  let store: Store
  beforeEach(() => {
    currentUser = {
      firstName: 'John',
      dateCreated: '2022-07-29T12:18:43.087097Z',
      email: 'john@do.net',
      id: '1',
      nonHumanizedId: '1',
      isAdmin: false,
      isEmailValidated: true,
      roles: [],
    }

    store = configureTestStore({
      user: {
        initialized: true,
        currentUser,
      },
    })
    jest.spyOn(api, 'getOfferer').mockResolvedValue({
      id: 'A1',
      managedVenues: [
        { id: 'V1', name: 'Salle 1' },
        { id: 'V2', name: 'Stand popcorn' },
      ],
    } as GetOffererResponseModel)
    jest.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [
        {
          id: 'A1',
          name: 'Mon super cinéma',
        },
        {
          id: 'B1',
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
    renderOffererStats(store)

    await waitFor(() => {
      expect(api.listOfferersNames).toHaveBeenCalledTimes(1)
    })
    const offererOption = screen.getByText('Mon super cinéma')
    expect(offererOption).toBeInTheDocument()
  })

  it('should display error message if api call fail', async () => {
    const notifyError = jest.fn()
    // @ts-ignore
    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
      error: notifyError,
    }))
    jest.spyOn(api, 'listOfferersNames').mockRejectedValueOnce('')
    renderOffererStats(store)

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
