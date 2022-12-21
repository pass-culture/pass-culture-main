import '@testing-library/jest-dom'

import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { Events, VenueEvents } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import { configureTestStore } from 'store/testUtils'
import { loadFakeApiVenueStats } from 'utils/fakeApi'

import Venue, { IVenueProps } from '../Venue'

const mockLogEvent = jest.fn()

const renderVenue = async (props: IVenueProps) => {
  const store = configureTestStore()
  return render(
    <Provider store={store}>
      <MemoryRouter>
        <Venue {...props} />
      </MemoryRouter>
    </Provider>
  )
}

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
  let props: IVenueProps

  beforeEach(() => {
    props = {
      id: 'VENUE01',
      isVirtual: false,
      name: 'My venue',
      offererId: 'OFFERER01',
    }
    loadFakeApiVenueStats({
      activeBookingsQuantity: 0,
      activeOffersCount: 2,
      soldOutOffersCount: 3,
      validatedBookingsQuantity: 1,
    })
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  it('should track with virtual param', async () => {
    // Given
    props.isVirtual = true

    // When
    await renderVenue(props)
    await userEvent.click(screen.getByTitle('Afficher'))
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    await userEvent.click(
      screen.getByRole('link', { name: 'Créer une nouvelle offre numérique' })
    )

    // Then
    expect(mockLogEvent).toHaveBeenCalledTimes(2)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      2,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'Home',
        isEdition: false,
        to: 'OfferFormHomepage',
        used: 'HomeVirtualLink',
      }
    )
  })

  it('should track with physical param', async () => {
    // Given
    props.isVirtual = false

    // When
    await renderVenue(props)
    await userEvent.click(screen.getByTitle('Afficher'))
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    await userEvent.click(
      screen.getByRole('link', { name: 'Créer une nouvelle offre' })
    )

    // Then
    expect(mockLogEvent).toHaveBeenCalledTimes(2)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      2,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'Home',
        isEdition: false,
        to: 'OfferFormHomepage',
        used: 'HomeLink',
      }
    )
  })

  it('should track updating venue', async () => {
    // Given
    props.isVirtual = false

    // When
    await renderVenue(props)
    await userEvent.click(screen.getByRole('link', { name: 'Modifier' }))

    // Then
    expect(mockLogEvent).toHaveBeenCalledWith(
      VenueEvents.CLICKED_VENUE_PUBLISHED_OFFERS_LINK,
      {
        venue_id: props.id,
      }
    )
  })

  it.each(trackerForVenue)(
    'should track event $event on click on link at $index',
    async ({ index, event }) => {
      props.isVirtual = true
      await renderVenue(props)

      await userEvent.click(screen.getByRole('button', { name: 'Afficher' }))
      expect(mockLogEvent).toHaveBeenCalledWith(
        VenueEvents.CLICKED_VENUE_ACCORDION_BUTTON,
        {
          venue_id: props.id,
        }
      )
      const stats = screen.getAllByTestId('venue-stat')
      await userEvent.click(
        within(stats[index]).getByRole('link', { name: 'Voir' })
      )
      expect(mockLogEvent).toHaveBeenCalledTimes(2)
      expect(mockLogEvent).toHaveBeenNthCalledWith(2, event, {
        venue_id: props.id,
      })
    }
  )
})
