import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

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

const mockLogEvent = vi.fn()

const renderVenueOfferSteps = (
  venueId: number | null = null,
  hasMissingReimbursementPoint = true,
  shouldDisplayEacSection = false,
  hasPendingBankInformationApplication = false,
  demarchesSimplifieesApplicationId?: number
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
      offererId={12}
      hasMissingReimbursementPoint={hasMissingReimbursementPoint}
      shouldDisplayEACInformationSection={shouldDisplayEacSection}
      hasPendingBankInformationApplication={
        hasPendingBankInformationApplication
      }
      demarchesSimplifieesApplicationId={demarchesSimplifieesApplicationId}
    />,
    { storeOverrides, initialRouterEntries: ['/accueil'] }
  )
}

describe('VenueOfferSteps', () => {
  const venueId = 1
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
    renderVenueOfferSteps(venueId)

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
    renderVenueOfferSteps(venueId)

    await userEvent.click(
      screen.getByText(/Renseigner des coordonnées bancaires/)
    )

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenCalledWith(
      VenueEvents.CLICKED_VENUE_ADD_RIB_BUTTON,
      {
        venue_id: venueId,
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

  it('should track click on dms timeline link', async () => {
    renderVenueOfferSteps(venueId, true, true)

    await userEvent.click(
      screen.getByText('Suivre ma demande de référencement ADAGE')
    )

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenCalledWith(Events.CLICKED_EAC_DMS_TIMELINE, {
      from: location.pathname,
    })
  })

  it('should track click on dms redirect link', async () => {
    renderVenueOfferSteps(venueId, false, false, true, 123456)

    await userEvent.click(
      screen.getByText('Suivre mon dossier de coordonnées bancaires')
    )

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenCalledWith(
      VenueEvents.CLICKED_BANK_DETAILS_RECORD_FOLLOW_UP,
      {
        from: location.pathname,
      }
    )
  })
})
