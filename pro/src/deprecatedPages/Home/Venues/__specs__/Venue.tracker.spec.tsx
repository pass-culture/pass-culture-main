import {
  screen,
  waitForElementToBeRemoved,
  within,
} from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { Events, VenueEvents } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import * as useNewOfferCreationJourney from 'hooks/useNewOfferCreationJourney'
import { loadFakeApiVenueStats } from 'utils/fakeApi'
import { renderWithProviders } from 'utils/renderWithProviders'

import Venue, { IVenueProps } from '../Venue'

const mockLogEvent = jest.fn()

const renderVenue = async (props: IVenueProps) =>
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
  let props: IVenueProps
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
    await userEvent.click(
      screen.getByTitle('Afficher les statistiques de My venue')
    )
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
    await userEvent.click(
      screen.getByTitle('Afficher les statistiques de My venue')
    )
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
    await jest
      .spyOn(useNewOfferCreationJourney, 'default')
      .mockReturnValue(true)
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

      await userEvent.click(
        screen.getByTitle('Afficher les statistiques de My venue')
      )
      expect(mockLogEvent).toHaveBeenCalledWith(
        VenueEvents.CLICKED_VENUE_ACCORDION_BUTTON,
        {
          venue_id: props.venueId,
        }
      )
      const stats = screen.getAllByTestId('venue-stat')
      await userEvent.click(
        within(stats[index]).getByRole('link', { name: 'Voir' })
      )
      expect(mockLogEvent).toHaveBeenCalledTimes(2)
      expect(mockLogEvent).toHaveBeenNthCalledWith(2, event, {
        venue_id: props.venueId,
      })
    }
  )
})
