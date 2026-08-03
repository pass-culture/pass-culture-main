import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import * as useAnalytics from 'app/App/analytics/firebase'
import { HeadlineOfferContextProvider } from 'commons/context/HeadlineOfferContext/HeadlineOfferContext'
import { getIndividualOfferFactory } from 'commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import {
  EngagementEvents,
  Events,
  INDIVIDUAL_OFFERS_NAVIGATION_SOURCE,
} from '@/commons/core/FirebaseEvents/constants'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'

import { api } from 'apiClient/api'
import { HeadlineOffer } from './HeadlineOffer'

describe('HeadlineOffer', () => {
  it('should log when cultural actor click on see in app', async () => {
    const mockLogEvent = vi.fn()
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    vi.spyOn(api, 'getVenueHeadlineOffer').mockResolvedValue({
      id: 42,
      name: 'My offer',
      venueId: 1,
    })

    vi.spyOn(api, 'getOffer').mockResolvedValue(
      getIndividualOfferFactory({ id: 42 })
    )

    const user = sharedCurrentUserFactory()
    renderWithProviders(
      <HeadlineOfferContextProvider>
        <HeadlineOffer />
      </HeadlineOfferContextProvider>,
      {
        user,
        storeOverrides: {
          user: {
            currentUser: user,
            selectedPartnerVenue: makeGetVenueResponseModel({ id: 2 }),
          },
        },
      }
    )

    await userEvent.click(
      await screen.findByText('Visualiser dans l’application')
    )

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      EngagementEvents.CLICKED_CONFIRMED_ADD_HEADLINE_OFFER,
      {
        offerId: 42,
        action: 'seeInApp',
      }
    )
  })
  it('should log when cultural actor click on see in app and offer link', async () => {
    const mockLogEvent = vi.fn()
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    vi.spyOn(api, 'getVenueHeadlineOffer').mockResolvedValue({
      id: 42,
      name: 'My offer',
      venueId: 1,
    })

    vi.spyOn(api, 'getOffer').mockResolvedValue(
      getIndividualOfferFactory({ id: 42 })
    )

    const user = sharedCurrentUserFactory()
    renderWithProviders(
      <HeadlineOfferContextProvider>
        <HeadlineOffer />
      </HeadlineOfferContextProvider>,
      {
        user,
        storeOverrides: {
          user: {
            currentUser: user,
            selectedPartnerVenue: makeGetVenueResponseModel({ id: 2 }),
          },
        },
      }
    )

    await userEvent.click(
      await screen.findByText('Visualiser dans l’application')
    )

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      EngagementEvents.CLICKED_CONFIRMED_ADD_HEADLINE_OFFER,
      {
        offerId: 42,
        action: 'seeInApp',
      }
    )

    await userEvent.click(await screen.findByText('My offer'))

    expect(mockLogEvent).toHaveBeenCalledTimes(2)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      2,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        offerId: 42,
        used: INDIVIDUAL_OFFERS_NAVIGATION_SOURCE.HEADLINE_OFFER,
      }
    )
  })
})
