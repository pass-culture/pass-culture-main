import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import { CancelablePromise, GetOffererResponseModel } from 'apiClient/v1'
import { Option } from 'core/Offers/types'
import { renderWithProviders } from 'utils/renderWithProviders'

import OffererStatsScreen from '../OffererStatsScreen'

jest.mock('apiClient/api', () => ({
  api: {
    getOfferer: jest.fn(),
    getOffererStatsDashboardUrl: jest.fn(),
    getVenueStatsDashboardUrl: jest.fn(),
  },
}))

const renderOffererStatsScreen = (offererOptions: Option[]) => {
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

  renderWithProviders(<OffererStatsScreen offererOptions={offererOptions} />, {
    storeOverrides,
  })
}

describe('OffererStatsScreen', () => {
  let offererOptions: Option[]
  let offerers: GetOffererResponseModel[]
  const venueId = 1

  beforeEach(() => {
    offererOptions = [
      {
        id: '1',
        displayName: 'Mon super cinéma',
      },
      {
        id: '2',
        displayName: 'Ma super librairie',
      },
    ]
    offerers = [
      {
        nonHumanizedId: 1,
        hasDigitalVenueAtLeastOneOffer: true,
        managedVenues: [
          {
            id: 'D1',
            name: 'Offre numérique',
            isVirtual: true,
            nonHumanizedId: venueId,
          },
          { id: 'V1', name: 'Salle 1', nonHumanizedId: 2 },
          { id: 'V2', name: 'Stand popcorn', nonHumanizedId: 3 },
        ],
      },
      {
        nonHumanizedId: 2,
        managedVenues: [
          { id: 'L1', name: 'Terre de livres', nonHumanizedId: 4 },
          { id: 'L2', name: 'La voie aux chapitres', nonHumanizedId: 5 },
        ],
      },
    ] as GetOffererResponseModel[]

    jest.spyOn(api, 'getOfferer').mockImplementation(offererId => {
      return new CancelablePromise(resolve =>
        resolve(
          offerers.filter(offerer => offerer.nonHumanizedId == offererId)[0]
        )
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
    renderOffererStatsScreen(offererOptions)

    await waitFor(() => {
      expect(api.getOfferer).toHaveBeenCalledTimes(1)
    })
    const virtualVenueOption = await screen.findByText('Offre numérique')
    const venueOption = screen.getByText('Salle 1')
    expect(virtualVenueOption).toBeInTheDocument()
    expect(venueOption).toBeInTheDocument()
  })

  it('should not display virtual venue if offerer has no digital offer', async () => {
    offerers[0].hasDigitalVenueAtLeastOneOffer = false
    renderOffererStatsScreen(offererOptions)

    await waitFor(() => {
      expect(api.getOfferer).toHaveBeenCalledTimes(1)
    })
    const venueOption = await screen.findByText('Salle 1')
    const virtualVenueOption = screen.queryByText('Offre numérique')
    expect(virtualVenueOption).not.toBeInTheDocument()
    expect(venueOption).toBeInTheDocument()
  })

  it('should update venues  when selecting offerer and display offerer iframe', async () => {
    renderOffererStatsScreen(offererOptions)
    await waitFor(() => {
      expect(api.getOfferer).toHaveBeenCalledTimes(1)
    })
    const offererSelect = screen.getByLabelText('Structure')
    await userEvent.selectOptions(offererSelect, '2')

    const iframe = screen.getByTitle('Tableau des statistiques')
    expect(iframe).toBeInTheDocument()
    expect(iframe).toHaveAttribute('src', 'venueIframeUrl')

    expect(screen.getByText('Terre de livres')).toBeInTheDocument()
    expect(screen.getByText('La voie aux chapitres')).toBeInTheDocument()
  })

  it('should display not display venue select if offerer has no venue', async () => {
    jest
      .spyOn(api, 'getOfferer')
      .mockResolvedValue({ nonHumanizedId: 1 } as GetOffererResponseModel)
    renderOffererStatsScreen(offererOptions)
    await waitFor(() => {
      expect(api.getOfferer).toHaveBeenCalledTimes(1)
    })

    const venueSelect = screen.queryByLabelText('Lieu')
    expect(venueSelect).not.toBeInTheDocument()
  })

  it('should display venue iframe when selecting a venue', async () => {
    renderOffererStatsScreen(offererOptions)
    await waitFor(() => {
      expect(api.getOfferer).toHaveBeenCalledTimes(1)
    })

    const venueSelect = await screen.findByLabelText('Lieu')
    await userEvent.selectOptions(venueSelect, venueId.toString())
    const iframe = screen.getByTitle('Tableau des statistiques')
    expect(iframe).toBeInTheDocument()
    expect(iframe).toHaveAttribute('src', 'venueIframeUrl')
  })

  it('should display offerer stats when selecting all venues', async () => {
    renderOffererStatsScreen(offererOptions)
    await waitFor(() => {
      expect(api.getOfferer).toHaveBeenCalledTimes(1)
    })

    const venueSelect = await screen.findByLabelText('Lieu')
    await userEvent.selectOptions(venueSelect, 'all')
    expect(api.getOffererStatsDashboardUrl).toHaveBeenCalledTimes(1)
  })
})
