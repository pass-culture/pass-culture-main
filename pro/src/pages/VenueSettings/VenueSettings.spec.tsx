import { screen } from '@testing-library/react'

import { apiNew } from '@/apiClient/api'
import { defaultVenueProvider } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { Component as VenueSettings } from './VenueSettings'

const { mockVenueSettingsScreen } = vi.hoisted(() => ({
  mockVenueSettingsScreen: vi.fn(() => (
    <div data-testid="venue-settings-screen">Venue settings screen</div>
  )),
}))

vi.mock('./components/VenueSettingsScreen', () => ({
  VenueSettingsScreen: mockVenueSettingsScreen,
}))

vi.mock('@/apiClient/api', () => ({
  apiNew: {
    getVenue: vi.fn(),
    listVenueProviders: vi.fn(),
  },
}))

const selectedPartnerVenue = makeGetVenueResponseModel({ id: 1 })

const renderVenueSettings = (options?: RenderWithProvidersOptions) => {
  const user = sharedCurrentUserFactory()

  return renderWithProviders(<VenueSettings />, {
    user,
    ...options,
    storeOverrides: {
      user: {
        currentUser: user,
        selectedPartnerVenue,
      },
      ...options?.storeOverrides,
    },
  })
}

describe('VenueSettings', () => {
  it('should render VenueSettingsScreen when data is ready', async () => {
    const venue = makeGetVenueResponseModel({ id: 1 })

    vi.spyOn(apiNew, 'getVenue').mockResolvedValue(venue)
    vi.spyOn(apiNew, 'listVenueProviders').mockResolvedValue({
      venueProviders: [{ ...defaultVenueProvider }],
    })

    renderVenueSettings()

    expect(
      await screen.findByTestId('venue-settings-screen')
    ).toBeInTheDocument()
    expect(screen.queryByTestId('spinner')).not.toBeInTheDocument()
    expect(apiNew.getVenue).toHaveBeenCalledWith({
      path: { venue_id: venue.id },
    })
    expect(apiNew.listVenueProviders).toHaveBeenCalledWith({
      path: { venue_id: venue.id },
    })

    expect(mockVenueSettingsScreen).toHaveBeenCalledWith(
      {
        offerer: selectedPartnerVenue.managingOfferer,
        venue,
        venueProviders: [{ ...defaultVenueProvider }],
      },
      undefined
    )
  })
})
