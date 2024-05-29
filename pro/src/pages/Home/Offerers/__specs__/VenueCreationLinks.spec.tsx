import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import * as useAnalytics from 'app/App/analytics/firebase'
import { Events } from 'core/FirebaseEvents/constants'
import {
  defaultGetOffererVenueResponseModel,
  defaultGetOffererResponseModel,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { VenueCreationLinks } from '../VenueCreationLinks'

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

    expect(screen.queryByText('Ajouter un lieu')).not.toBeInTheDocument()
  })

  it('should display creation links when user has a venue created', async () => {
    const offerer = {
      ...defaultGetOffererResponseModel,
      managedVenues: [defaultGetOffererVenueResponseModel],
    }

    renderWithProviders(<VenueCreationLinks offerer={offerer} />)

    await userEvent.click(screen.getByText('Ajouter un lieu'))

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
