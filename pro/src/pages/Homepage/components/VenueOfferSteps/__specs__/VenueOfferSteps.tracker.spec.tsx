import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import * as useAnalytics from 'app/App/analytics/firebase'
import { Events, VenueEvents } from 'commons/core/FirebaseEvents/constants'
import {
  defaultGetOffererVenueResponseModel,
  defaultGetOffererResponseModel,
} from 'commons/utils/factories/individualApiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'commons/utils/renderWithProviders'
import * as venueUtils from 'pages/Homepage/components/Offerers/components/VenueList/venueUtils'

import { VenueOfferSteps, VenueOfferStepsProps } from '../VenueOfferSteps'

const mockLogEvent = vi.fn()

const renderVenueOfferSteps = (
  props?: Partial<VenueOfferStepsProps>,
  options?: RenderWithProvidersOptions
) => {
  return renderWithProviders(
    <VenueOfferSteps
      hasVenue={false}
      offerer={{
        ...defaultGetOffererResponseModel,
        hasPendingBankAccount: false,
        hasValidBankAccount: false,
        hasNonFreeOffer: false,
      }}
      {...props}
    />,
    { initialRouterEntries: ['/accueil'], ...options }
  )
}

describe('VenueOfferSteps', () => {
  const venueId = 1
  const venue = {
    ...defaultGetOffererVenueResponseModel,
    id: venueId,
  }

  beforeEach(() => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    vi.spyOn(
      venueUtils,
      'shouldDisplayEACInformationSectionForVenue'
    ).mockReturnValue(true)
  })

  it('should track creation venue', async () => {
    renderVenueOfferSteps()

    await userEvent.click(screen.getByText(/Créer une structure/))

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
    renderVenueOfferSteps({ venue, hasVenue: true })

    await userEvent.click(screen.getByText(/Créer une offre/))
  })

  it('should track ReimbursementPoint', async () => {
    renderVenueOfferSteps({
      venue: { ...venue },
      hasVenue: true,
    })

    await userEvent.click(screen.getByText(/Ajouter un compte bancaire/))

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
        /Je ne dispose pas de structure propre, quel type de structure créer ?/
      )
    )

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenCalledWith(Events.CLICKED_NO_VENUE, {
      from: location.pathname,
    })
  })

  it('should track click on dms timeline link', async () => {
    renderVenueOfferSteps({
      venue: { ...venue },
      hasVenue: true,
    })

    await userEvent.click(
      screen.getByText('Suivre ma demande de référencement ADAGE')
    )

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenCalledWith(Events.CLICKED_EAC_DMS_TIMELINE, {
      from: location.pathname,
    })
  })
})
