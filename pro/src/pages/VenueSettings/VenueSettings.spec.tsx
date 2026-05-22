import { screen } from '@testing-library/react'

import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { VenueSettings } from './VenueSettings'

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
  it('should render the settings page heading', () => {
    renderVenueSettings()

    expect(screen.getByText('Paramètres généraux')).toBeInTheDocument()
  })
})
