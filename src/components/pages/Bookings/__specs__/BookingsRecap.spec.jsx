import '@testing-library/jest-dom'
import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { getVenuesForOfferer, loadFilteredBookingsRecap } from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'
import { bookingRecapFactory, venueFactory } from 'utils/apiFactories'

import BookingsRecapContainer from '../BookingsRecapContainer'

jest.mock('repository/pcapi/pcapi', () => ({
  getVenuesForOfferer: jest.fn(),
  loadFilteredBookingsRecap: jest.fn(),
}))

const renderBookingsRecap = async (props, store = {}) => {
  await act(async () => {
    await render(
      <Provider store={store}>
        <MemoryRouter>
          <BookingsRecapContainer {...props} />
        </MemoryRouter>
      </Provider>
    )
  })
}

describe('components | BookingsRecap', () => {
  let props
  let store
  let venue

  beforeEach(() => {
    let emptyBookingsRecapPage = {
      bookings_recap: [],
      page: 0,
      pages: 0,
      total: 0,
    }
    loadFilteredBookingsRecap.mockResolvedValue(emptyBookingsRecapPage)
    props = {
      location: {
        state: null,
      },
    }
    store = configureTestStore({
      data: {
        features: [
          {
            isActive: true,
            name: 'ENABLE_BOOKINGS_PAGE_FILTERS_FIRST',
            nameKey: 'ENABLE_BOOKINGS_PAGE_FILTERS_FIRST',
          },
        ],
        users: [{ publicName: 'René', isAdmin: false, email: 'rené@example.com' }],
      },
    })
    venue = venueFactory()
    getVenuesForOfferer.mockResolvedValue([venue])
  })

  it('should show a pre-filter section', async () => {
    // When
    await renderBookingsRecap(props, store)

    // Then
    const eventDateFilter = screen.getByLabelText('Date de l’évènement')
    const eventVenueFilter = screen.getByLabelText('Lieu')
    const eventBookingPeriodFilter = screen.getByLabelText('Période de réservation')
    expect(eventDateFilter).toBeInTheDocument()
    expect(eventVenueFilter).toBeInTheDocument()
    expect(eventBookingPeriodFilter).toBeInTheDocument()
  })

  it('should request bookings of venue filtered by user when user clicks on "Afficher"', async () => {
    // Given
    await renderBookingsRecap(props, store)

    // When
    userEvent.selectOptions(screen.getByLabelText('Lieu'), venue.id)
    userEvent.click(screen.getByText('Afficher', { selector: 'button' }))

    // Then
    expect(loadFilteredBookingsRecap).toHaveBeenCalledWith({ page: 1, venueId: venue.id })
  })

  it('should fetch bookings for the filtered venue as many times as the number of pages', async () => {
    // Given
    const bookings1 = bookingRecapFactory()
    const bookings2 = bookingRecapFactory()
    const emptyPageReturned = {
      page: 1,
      pages: 1,
      total: 0,
      bookings_recap: [],
    }
    const paginatedBookingRecapReturned = {
      page: 1,
      pages: 2,
      total: 2,
      bookings_recap: [bookings1],
    }
    const secondPaginatedBookingRecapReturned = {
      page: 2,
      pages: 2,
      total: 2,
      bookings_recap: [bookings2],
    }
    loadFilteredBookingsRecap
      .mockResolvedValueOnce(emptyPageReturned)
      .mockResolvedValueOnce(paginatedBookingRecapReturned)
      .mockResolvedValueOnce(secondPaginatedBookingRecapReturned)
    await renderBookingsRecap(props, store)

    // When
    userEvent.selectOptions(screen.getByLabelText('Lieu'), venue.id)
    await userEvent.click(screen.getByText('Afficher', { selector: 'button' }))

    // Then
    const secondBookingRecap = await screen.findAllByText(bookings2.stock.offer_name)
    expect(secondBookingRecap).toHaveLength(2)
    const firstBookingRecap = screen.getAllByText(bookings1.stock.offer_name)
    expect(firstBookingRecap).toHaveLength(2)

    expect(loadFilteredBookingsRecap).toHaveBeenCalledTimes(3)
    expect(loadFilteredBookingsRecap).toHaveBeenNthCalledWith(2, {page:1, venueId: venue.id })
    expect(loadFilteredBookingsRecap).toHaveBeenNthCalledWith(3, {page:2, venueId: venue.id })
  })

  it('should reset bookings recap list when applying filters', async () => {
    // Given
    const booking = bookingRecapFactory()
    const otherVenueBooking = bookingRecapFactory()
    const otherVenue = venueFactory()
    getVenuesForOfferer.mockResolvedValue([venue, otherVenue])
    const emptyPageReturned = {
      page: 1,
      pages: 1,
      total: 0,
      bookings_recap: [],
    }
    const paginatedBookingRecapReturned = {
      page: 1,
      pages: 1,
      total: 1,
      bookings_recap: [booking],
    }
    const otherVenuePaginatedBookingRecapReturned = {
      page: 1,
      pages: 1,
      total: 1,
      bookings_recap: [otherVenueBooking],
    }
    loadFilteredBookingsRecap
      .mockResolvedValueOnce(emptyPageReturned)
      .mockResolvedValueOnce(otherVenuePaginatedBookingRecapReturned)
      .mockResolvedValueOnce(paginatedBookingRecapReturned)
    await renderBookingsRecap(props, store)

    userEvent.selectOptions(screen.getByLabelText('Lieu'), otherVenue.id)
    userEvent.click(screen.getByText('Afficher', { selector: 'button' }))
    await screen.findAllByText(otherVenueBooking.stock.offer_name)

    // When
    userEvent.selectOptions(screen.getByLabelText('Lieu'), venue.id)
    await userEvent.click(screen.getByText('Afficher', { selector: 'button' }))

    // Then
    const firstBookingRecap = await screen.findAllByText(booking.stock.offer_name)
    expect(firstBookingRecap).toHaveLength(2)
    expect(screen.queryByText(otherVenueBooking.stock.offer_name)).not.toBeInTheDocument()
  })
})
