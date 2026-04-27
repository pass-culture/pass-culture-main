import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import * as useAnalytics from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { VenueOfferSteps } from '../VenueOfferSteps'

const mockLogEvent = vi.fn()

const renderVenueOfferSteps = () =>
  renderWithProviders(<VenueOfferSteps />, {
    initialRouterEntries: ['/accueil'],
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
        selectedPartnerVenue: defaultGetVenue,
      },
    },
  })

describe('VenueOfferSteps tracking', () => {
  beforeEach(() => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  it('should log CLICKED_EAC_DMS_TIMELINE when clicking on the DMS timeline link', async () => {
    renderVenueOfferSteps()

    await userEvent.click(
      screen.getByRole('link', {
        name: 'Suivre ma demande de référencement ADAGE',
      })
    )

    expect(mockLogEvent).toHaveBeenCalledExactlyOnceWith(
      Events.CLICKED_EAC_DMS_TIMELINE
    )
  })
})
