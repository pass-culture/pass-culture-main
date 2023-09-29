import {
  screen,
  waitForElementToBeRemoved,
  within,
} from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import { VenueEvents } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import { renderWithProviders } from 'utils/renderWithProviders'

import Venue, { VenueProps } from '../Venue'

const mockLogEvent = vi.fn()

vi.mock('apiClient/api', () => ({
  api: {
    getVenueStats: vi.fn(),
  },
}))

const renderVenue = async (props: VenueProps) =>
  renderWithProviders(<Venue {...props} />)

const trackerForVenue = [
  {
    index: 0,
    event: VenueEvents.CLICKED_VENUE_PUBLISHED_OFFERS_LINK,
  },
  {
    index: 1,
    event: VenueEvents.CLICKED_VENUE_ACTIVE_BOOKINGS_LINK,
  },
  {
    index: 2,
    event: VenueEvents.CLICKED_VENUE_VALIDATED_RESERVATIONS_LINK,
  },
  {
    index: 3,
    event: VenueEvents.CLICKED_VENUE_EMPTY_STOCK_LINK,
  },
]

describe('venue create offer link', () => {
  let props: VenueProps
  const venueId = 1
  const offererId = 12

  beforeEach(() => {
    props = {
      venueId: venueId,
      isVirtual: false,
      name: 'My venue',
      offererId: offererId,
      dmsInformations: null,
    }
    vi.spyOn(api, 'getVenueStats').mockResolvedValue({
      activeBookingsQuantity: 0,
      activeOffersCount: 2,
      soldOutOffersCount: 3,
      validatedBookingsQuantity: 1,
    })
    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  it('should track with virtual param', async () => {
    // Given
    props.isVirtual = true

    // When
    await renderVenue(props)
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    await userEvent.click(
      screen.getByRole('link', { name: 'Créer une nouvelle offre numérique' })
    )
  })

  it('should track with physical param', async () => {
    // Given
    props.isVirtual = false

    // When
    await renderVenue(props)
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    await userEvent.click(
      screen.getByRole('link', { name: 'Créer une nouvelle offre' })
    )
  })

  it('should track updating venue', async () => {
    // Given
    props.isVirtual = false

    // When
    await renderVenue(props)
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    await userEvent.click(screen.getByRole('link', { name: 'Éditer le lieu' }))

    // Then
    expect(mockLogEvent).toHaveBeenCalledWith(
      VenueEvents.CLICKED_VENUE_PUBLISHED_OFFERS_LINK,
      {
        venue_id: props.venueId,
      }
    )
  })

  it('should track Add RIB button', async () => {
    // Given
    props.isVirtual = false
    props.hasMissingReimbursementPoint = true
    props.hasCreatedOffer = true

    // When
    await renderVenue(props)
    await userEvent.click(screen.getByRole('link', { name: 'Ajouter un RIB' }))

    // Then
    expect(mockLogEvent).toHaveBeenCalledWith(
      VenueEvents.CLICKED_VENUE_ADD_RIB_BUTTON,
      {
        from: '/',
        venue_id: props.venueId,
      }
    )
  })

  it('should track updating venue with new venue creation journey', async () => {
    // Given
    props.isVirtual = false

    // When
    await renderVenue(props)
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))
    expect(
      screen.getByRole('link', { name: 'Éditer le lieu' })
    ).toHaveAttribute(
      'href',
      `/structures/${offererId}/lieux/${venueId}?modification`
    )
  })

  it.each(trackerForVenue)(
    'should track event $event on click on link at $index',
    async ({ index, event }) => {
      props.isVirtual = true
      await renderVenue(props)
      await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

      const stats = screen.getAllByTestId('venue-stat')
      await userEvent.click(
        within(stats[index]).getByRole('link', { name: /Voir/ })
      )
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(1, event, {
        venue_id: props.venueId,
      })
    }
  )
})
