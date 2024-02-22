import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { VenueEvents } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
} from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { Venue, VenueProps } from '../Venue'

const mockLogEvent = vi.fn()

const renderVenue = (props: VenueProps) =>
  renderWithProviders(<Venue {...props} />)

describe('venue create offer link', () => {
  let props: VenueProps
  const venueId = 1
  const offererId = 12

  beforeEach(() => {
    props = {
      offerer: { ...defaultGetOffererResponseModel, id: offererId },
      venue: {
        ...defaultGetOffererVenueResponseModel,
        id: venueId,
        name: 'My venue',
      },
      isFirstVenue: false,
    }
    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  it('should track updating venue', async () => {
    props.venue.isVirtual = false

    renderVenue(props)

    await userEvent.click(
      screen.getByRole('link', { name: `Gérer la page de My venue` })
    )

    expect(mockLogEvent).toHaveBeenCalledWith(
      VenueEvents.CLICKED_VENUE_PUBLISHED_OFFERS_LINK,
      { venue_id: props.venue.id }
    )
  })

  it('should track Add RIB button', async () => {
    props.venue.isVirtual = false
    props.venue.hasMissingReimbursementPoint = true
    props.venue.hasCreatedOffer = true

    renderVenue(props)
    await userEvent.click(screen.getByRole('link', { name: 'Ajouter un RIB' }))

    expect(mockLogEvent).toHaveBeenCalledWith(
      VenueEvents.CLICKED_VENUE_ADD_RIB_BUTTON,
      {
        from: '/',
        venue_id: props.venue.id,
      }
    )
  })

  it('should track updating venue with new venue creation journey', () => {
    props.venue.isVirtual = false

    renderVenue(props)

    expect(
      screen.getByRole('link', { name: `Gérer la page de My venue` })
    ).toHaveAttribute('href', `/structures/${offererId}/lieux/${venueId}`)
  })
})
