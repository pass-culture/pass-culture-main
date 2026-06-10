import { screen } from '@testing-library/react'
import type { SWRResponse } from 'swr'

import type { GetVenueResponseModel } from '@/apiClient/v1/new'
import * as useEducationalDomainsModule from '@/commons/hooks/swr/useEducationalDomains'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { IndividualVenuePage } from './IndividualVenuePage'

const renderIndividualVenuePage = (
  venueOverrides: Partial<GetVenueResponseModel> = {}
) =>
  renderWithProviders(<IndividualVenuePage />, {
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

describe('IndividualVenuePage', () => {
  beforeEach(() => {
    vi.spyOn(
      useEducationalDomainsModule,
      'useEducationalDomains'
    ).mockReturnValue({ isLoading: false, data: [] } as SWRResponse)
  })

  it('should warn that the page is invisible when a permanent venue with offers has no active individual offer', () => {
    renderIndividualVenuePage({
      isPermanent: true,
      hasOffers: true,
      hasActiveIndividualOffer: false,
    })

    expect(screen.getByText('Page invisible')).toBeInTheDocument()
    expect(screen.getByText('Vos informations')).toBeInTheDocument()
  })

  it('should not warn when the venue has an active individual offer', () => {
    renderIndividualVenuePage({
      isPermanent: true,
      hasOffers: true,
      hasActiveIndividualOffer: true,
    })

    expect(screen.queryByText('Page invisible')).not.toBeInTheDocument()
  })
})
