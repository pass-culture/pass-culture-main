import '@testing-library/jest-dom'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import type { Store } from 'redux'

import { api } from 'apiClient/api'
import { CancelablePromise, GetOffererResponseModel } from 'apiClient/v1'
import { Option } from 'core/Offers/types'
import { configureTestStore } from 'store/testUtils'

import OffererStatsScreen from '../OffererStatsScreen'

jest.mock('apiClient/api', () => ({
  api: {
    getOfferer: jest.fn(),
    getOffererStatsDashboardUrl: jest.fn(),
    getVenueStatsDashboardUrl: jest.fn(),
  },
}))

const renderOffererStatsScreen = (offererOptions: Option[], store: Store) => {
  render(
    <Provider store={store}>
      <OffererStatsScreen offererOptions={offererOptions} />
    </Provider>
  )
}

describe('OffererStatsScreen', () => {
  let currentUser
  let offererOptions: Option[]
  let offerers: GetOffererResponseModel[]
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
    offererOptions = [
      {
        id: 'A1',
        displayName: 'Mon super cinéma',
      },
      {
        id: 'B1',
        displayName: 'Ma super librairie',
      },
    ]
    offerers = [
      {
        id: 'A1',
        hasDigitalVenueAtLeastOneOffer: true,
        managedVenues: [
          { id: 'D1', name: 'Offre numérique', isVirtual: true },
          { id: 'V1', name: 'Salle 1' },
          { id: 'V2', name: 'Stand popcorn' },
        ],
      },
      {
        id: 'B1',
        managedVenues: [
          { id: 'L1', name: 'Terre de livres' },
          { id: 'L2', name: 'La voie aux chapitres' },
        ],
      },
    ] as GetOffererResponseModel[]

    store = configureTestStore({
      user: {
        initialized: true,
        currentUser,
      },
    })
    jest.spyOn(api, 'getOfferer').mockImplementation(offererId => {
      return new CancelablePromise(resolve =>
        resolve(offerers.filter(offerer => offerer.id == offererId)[0])
      )
    })
    jest
      .spyOn(api, 'getOffererStatsDashboardUrl')
      .mockResolvedValue({ dashboardUrl: 'offererIframeUrl' })
    jest
      .spyOn(api, 'getVenueStatsDashboardUrl')
      .mockResolvedValue({ dashboardUrl: 'venueIframeUrl' })
  })

  it('should get first offerer venues on render', async () => {
    renderOffererStatsScreen(offererOptions, store)

    await waitFor(() => {
      expect(api.getOfferer).toHaveBeenCalledTimes(1)
    })
    const virtualVenueOption = screen.getByText('Offre numérique')
    const venueOption = screen.getByText('Salle 1')
    expect(virtualVenueOption).toBeInTheDocument()
    expect(venueOption).toBeInTheDocument()
  })
  it('should not display virtual venue if offerer has no digital offer', async () => {
    offerers[0].hasDigitalVenueAtLeastOneOffer = false
    renderOffererStatsScreen(offererOptions, store)

    await waitFor(() => {
      expect(api.getOfferer).toHaveBeenCalledTimes(1)
    })
    const virtualVenueOption = screen.queryByText('Offre numérique')
    const venueOption = screen.getByText('Salle 1')
    expect(virtualVenueOption).not.toBeInTheDocument()
    expect(venueOption).toBeInTheDocument()
  })
  it('should update venues  when selecting offerer and display offerer iframe', async () => {
    renderOffererStatsScreen(offererOptions, store)
    await waitFor(() => {
      expect(api.getOfferer).toHaveBeenCalledTimes(1)
    })
    const offererSelect = screen.getByLabelText('Structure')
    await userEvent.selectOptions(offererSelect, 'B1')

    const iframe = screen.getByTitle('Tableau des statistiques')
    expect(iframe).toBeInTheDocument()
    expect(iframe).toHaveAttribute('src', 'offererIframeUrl')

    expect(screen.getByText('Terre de livres')).toBeInTheDocument()
    expect(screen.getByText('La voie aux chapitres')).toBeInTheDocument()
  })
  it('should display not display venue select if offerer has no venue', async () => {
    jest
      .spyOn(api, 'getOfferer')
      .mockResolvedValue({ id: 'A1' } as GetOffererResponseModel)
    renderOffererStatsScreen(offererOptions, store)
    await waitFor(() => {
      expect(api.getOfferer).toHaveBeenCalledTimes(1)
    })

    const venueSelect = screen.queryByLabelText('Lieu')
    expect(venueSelect).not.toBeInTheDocument()
  })
  it('should display venue iframe when selecting a venue', async () => {
    renderOffererStatsScreen(offererOptions, store)
    await waitFor(() => {
      expect(api.getOfferer).toHaveBeenCalledTimes(1)
    })

    const venueSelect = screen.getByLabelText('Lieu')
    await userEvent.selectOptions(venueSelect, 'V1')
    const iframe = screen.getByTitle('Tableau des statistiques')
    expect(iframe).toBeInTheDocument()
    expect(iframe).toHaveAttribute('src', 'venueIframeUrl')
  })
})
