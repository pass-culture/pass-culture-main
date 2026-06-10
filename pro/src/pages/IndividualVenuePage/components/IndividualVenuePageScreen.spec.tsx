import { screen } from '@testing-library/react'
import type { SWRResponse } from 'swr'

import type { GetVenueResponseModel } from '@/apiClient/v1/new'
import * as useEducationalDomainsModule from '@/commons/hooks/swr/useEducationalDomains'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { formatPhoneNumber } from '@/commons/utils/formatPhoneNumber'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { IndividualVenuePageScreen } from './IndividualVenuePageScreen'

const renderScreen = (venueOverrides: Partial<GetVenueResponseModel> = {}) =>
  renderWithProviders(<IndividualVenuePageScreen />, {
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
        selectedPartnerVenue: makeGetVenueResponseModel({
          id: 1,
          ...venueOverrides,
        }),
      },
    },
  })

describe('IndividualVenuePageScreen', () => {
  beforeEach(() => {
    vi.spyOn(
      useEducationalDomainsModule,
      'useEducationalDomains'
    ).mockReturnValue({ isLoading: false, data: [] } as SWRResponse)
  })

  it('should display the venue information for an open-to-public venue', () => {
    renderScreen({
      isOpenToPublic: true,
      externalAccessibilityData: null,
      withdrawalDetails: 'Au comptoir',
      volunteeringUrl: 'https://benevolat.example.com',
      openingHours: { MONDAY: [['09:00', '12:00']] },
      contact: {
        phoneNumber: '0612345678',
        email: 'contact@example.com',
        website: 'https://example.com',
        socialMedias: null,
      },
    })

    expect(screen.getByText('Vos informations')).toBeInTheDocument()
    expect(screen.getByText(/Adresse :/)).toBeInTheDocument()
    expect(screen.getByText('Non accessible')).toBeInTheDocument()
    expect(screen.getByText('Au comptoir')).toBeInTheDocument()
    expect(
      screen.getByText('https://benevolat.example.com')
    ).toBeInTheDocument()
    expect(
      screen.getByText(formatPhoneNumber('0612345678'))
    ).toBeInTheDocument()
    expect(screen.getByText('contact@example.com')).toBeInTheDocument()
    expect(screen.getByText('https://example.com')).toBeInTheDocument()
  })

  it('should hide the address and accessibility sections and fall back to placeholders when closed to public and without contact', () => {
    renderScreen({
      isOpenToPublic: false,
      withdrawalDetails: null,
      volunteeringUrl: null,
      contact: null,
    })

    expect(screen.queryByText(/Adresse :/)).not.toBeInTheDocument()
    expect(screen.queryByText('Non accessible')).not.toBeInTheDocument()

    expect(screen.getAllByText('Non renseigné')).toHaveLength(2)
    expect(screen.getAllByText('Non renseignée')).toHaveLength(3)
  })
})
