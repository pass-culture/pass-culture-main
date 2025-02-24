import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import * as useAnalytics from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import {
  defaultGetOffererVenueResponseModel,
  defaultGetOffererResponseModel,
} from 'commons/utils/factories/individualApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { VenueCreationLinks } from './VenueCreationLinks'

const mockLogEvent = vi.fn()

describe('VenueCrationLinks', () => {
  beforeEach(() => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  it('should not display creation links when user has no venue created', () => {
    const offerer = {
      ...defaultGetOffererResponseModel,
      hasDigitalVenueAtLeastOneOffer: false,
      managedVenues: [],
    }

    renderWithProviders(<VenueCreationLinks offerer={offerer} />)

    expect(screen.queryByText('Ajouter une structure')).not.toBeInTheDocument()
  })

  it('should display creation links when user has a venue created', async () => {
    const offerer = {
      ...defaultGetOffererResponseModel,
      managedVenues: [defaultGetOffererVenueResponseModel],
    }

    renderWithProviders(<VenueCreationLinks offerer={offerer} />)

    await userEvent.click(screen.getByText('Ajouter une structure'))

    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_CREATE_VENUE,
      {
        from: '/',
        is_first_venue: true,
      }
    )
  })
})
