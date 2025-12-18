import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import type { VenueListItemResponseModel } from '@/apiClient/v1'
import {
  defaultGetOffererResponseModel,
  getOffererNameFactory,
  makeVenueListItem,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import {
  type RenderComponentFunction,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { Hub } from './Hub'

vi.mock('@/apiClient/api', () => ({
  api: {
    getOfferer: vi.fn(),
    getVenue: vi.fn(),
    signout: vi.fn(),
  },
}))

const renderHub: RenderComponentFunction<
  void,
  void,
  {
    venues: VenueListItemResponseModel[] | null
  }
> = ({ venues }) => {
  return renderWithProviders(<Hub />, {
    storeOverrides: {
      offerer: {
        currentOfferer: { ...defaultGetOffererResponseModel, id: 100 },
        currentOffererName: getOffererNameFactory({ id: 100 }),
        offererNames: [
          getOffererNameFactory({ id: 100 }),
          getOffererNameFactory({ id: 200 }),
        ],
      },
      user: {
        access: 'full',
        currentUser: sharedCurrentUserFactory(),
        selectedVenue: makeGetVenueResponseModel({
          id: 101,
          managingOfferer: {
            id: 100,
            allowedOnAdage: true,
            isValidated: true,
            name: 'Test Offerer',
            siren: '123456789',
          },
        }),
        venues,
      },
    },
    initialRouterEntries: ['/hub'],
  })
}

describe('Hub', () => {
  const venuesBase = [
    makeVenueListItem({ id: 101, name: 'Venue A', managingOffererId: 100 }),
    makeVenueListItem({ id: 102, name: 'Venue B', managingOffererId: 100 }),
    makeVenueListItem({ id: 201, name: 'Venue C', managingOffererId: 200 }),
  ]

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render the main heading', async () => {
    const { container } = renderHub({ venues: venuesBase })

    expect(await axe(container)).toHaveNoViolations()

    expect(
      screen.getByRole('heading', {
        level: 1,
        name: 'À quelle structure souhaitez-vous accéder ?',
      })
    ).toBeInTheDocument()
  })

  it('should render all venue buttons', () => {
    renderHub({ venues: venuesBase })

    expect(screen.getByRole('button', { name: /Venue A/ })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Venue B/ })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Venue C/ })).toBeInTheDocument()
  })

  it('should display venue address when location is available', () => {
    const venuesWithLocation = [
      makeVenueListItem({
        id: 101,
        name: 'Venue With Location',
        managingOffererId: 100,
        location: {
          id: 1,
          street: '123 Rue de Test',
          postalCode: '75001',
          city: 'Paris',
          latitude: 48.8566,
          longitude: 2.3522,
          isManualEdition: false,
          isVenueLocation: false,
        },
      }),
    ]

    renderHub({ venues: venuesWithLocation })

    expect(screen.getByText('123 Rue de Test, 75001 Paris')).toBeInTheDocument()
  })

  it('should not display venue address when location is unavailable', () => {
    const venuesWithoutAddress = [
      makeVenueListItem({
        id: 101,
        name: 'Venue Without Location',
        managingOffererId: 100,
        location: undefined,
      }),
    ]

    renderHub({ venues: venuesWithoutAddress })

    expect(
      screen.getByRole('button', { name: 'Venue Without Location' })
    ).toHaveTextContent('Venue Without Location')
  })

  it('should call setSelectedVenueById when clicking on any venue', async () => {
    vi.spyOn(api, 'getVenue').mockResolvedValue(
      makeGetVenueResponseModel({
        id: 102,
        managingOfferer: {
          id: 100,
          allowedOnAdage: true,
          isValidated: true,
          name: 'Test Offerer',
          siren: '123456789',
        },
      })
    )
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      id: 100,
      isOnboarded: true,
    })

    renderHub({ venues: venuesBase })

    const venueBButton = screen.getByRole('button', { name: 'Venue B' })
    await userEvent.click(venueBButton)

    await waitFor(() => {
      expect(api.getVenue).toHaveBeenCalledWith(102)
    })
  })
})
