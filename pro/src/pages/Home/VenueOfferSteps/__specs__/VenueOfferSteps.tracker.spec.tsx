import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { DMSApplicationstatus } from 'apiClient/v1'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  Events,
  OFFER_FORM_HOMEPAGE,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
  VenueEvents,
} from '../../../../core/FirebaseEvents/constants'
import * as useAnalytics from '../../../../hooks/useAnalytics'
import { VenueOfferSteps } from '../index'

const mockLogEvent = jest.fn()

const renderVenueOfferSteps = (
  venueId: string | null = null,
  hasMissingReimbursementPoint = true,
  dmsStatus: DMSApplicationstatus = DMSApplicationstatus.ACCEPTE,
  dmsInProgress = false
) => {
  const currentUser = {
    id: 'EY',
  }
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser,
    },
  }

  return renderWithProviders(
    <VenueOfferSteps
      hasVenue={venueId != null}
      venueId={venueId}
      offererId="AB"
      hasMissingReimbursementPoint={hasMissingReimbursementPoint}
      dmsStatus={dmsStatus}
      dmsInProgress={dmsInProgress}
    />,
    { storeOverrides, initialRouterEntries: ['/accueil'] }
  )
}

describe('VenueOfferSteps', () => {
  beforeEach(() => {
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })
  it('should track creation venue', async () => {
    renderVenueOfferSteps()

    await userEvent.click(screen.getByText(/Créer un lieu/))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_CREATE_VENUE,
      {
        from: '/',
        is_first_venue: true,
      }
    )
  })

  it('should track creation offer', async () => {
    renderVenueOfferSteps('venueId')

    await userEvent.click(screen.getByText(/Créer une offre/))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenCalledWith(
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: OFFER_FORM_NAVIGATION_IN.HOME,
        to: OFFER_FORM_HOMEPAGE,
        used: OFFER_FORM_NAVIGATION_MEDIUM.VENUE_OFFER_STEPS,
        isEdition: false,
      }
    )
  })

  it('should track ReimbursementPoint', async () => {
    renderVenueOfferSteps('venueId')

    await userEvent.click(
      screen.getByText(/Renseigner des coordonnées bancaires/)
    )

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenCalledWith(
      VenueEvents.CLICKED_VENUE_ADD_RIB_BUTTON,
      {
        venue_id: 'venueId',
        from: 'Home',
      }
    )
  })

  it('should track "I have no venue"', async () => {
    renderVenueOfferSteps()

    await userEvent.click(
      screen.getByText(
        /Je ne dispose pas de lieu propre, quel type de lieu créer ?/
      )
    )

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenCalledWith(Events.CLICKED_NO_VENUE, {
      from: location.pathname,
    })
  })
})
