import '@testing-library/jest-dom'
import { act, render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { loadFilteredBookingsRecap } from '../../../../repository/pcapi/pcapi'
import { configureTestStore } from '../../../../store/testUtils'
import { bookingRecapFactory } from '../../../../utils/apiFactories'
import BookingsRecapContainer from '../BookingsRecapContainer'

jest.mock('repository/pcapi/pcapi', () => ({
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

describe('components | BookingsRecapLegacy', () => {
  let props
  let store

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
            isActive: false,
            name: 'ENABLE_BOOKINGS_PAGE_FILTERS_FIRST',
            nameKey: 'ENABLE_BOOKINGS_PAGE_FILTERS_FIRST',
          },
        ],
        users: [{ publicName: 'René', isAdmin: false, email: 'rené@example.com' }],
      },
    })
  })

  it('should show NoBookingsMessage when api returned no bookings', async () => {
    // When
    await renderBookingsRecap(props, store)

    // Then
    const title = screen.getByText('Réservations', { selector: 'h1' })
    expect(title).toBeInTheDocument()
    const bookingsTable = screen.queryByText('Télécharger le CSV')
    expect(bookingsTable).not.toBeInTheDocument()
    const noBookingsMessage = screen.getByText('Aucune réservation pour le moment')
    expect(noBookingsMessage).toBeInTheDocument()
    const spinner = screen.queryByText('Chargement en cours')
    expect(spinner).not.toBeInTheDocument()
  })

  it('should render a bookings recap table when api returned at least one booking', async () => {
    // Given
    const oneBooking = bookingRecapFactory()
    const paginatedBookingRecapReturned = {
      page: 1,
      pages: 1,
      total: 1,
      bookings_recap: [oneBooking],
    }
    loadFilteredBookingsRecap.mockResolvedValue(paginatedBookingRecapReturned)

    // When
    await renderBookingsRecap(props, store)

    // Then
    const title = screen.getByText('Réservations', { selector: 'h1' })
    expect(title).toBeInTheDocument()
    const bookingsTable = screen.getByText('Télécharger le CSV')
    expect(bookingsTable).toBeInTheDocument()
    const bookingRecap = screen.getAllByText(oneBooking.stock.offer_name)
    expect(bookingRecap).toHaveLength(2)
    const noBookingsMessage = screen.queryByText('Aucune réservation pour le moment')
    expect(noBookingsMessage).not.toBeInTheDocument()
    const spinner = screen.queryByText('Chargement en cours')
    expect(spinner).not.toBeInTheDocument()
  })

  it('should fetch bookings as many times as the number of pages', async () => {
    // Given
    const bookings1 = bookingRecapFactory()
    const bookings2 = bookingRecapFactory()
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
      .mockResolvedValueOnce(paginatedBookingRecapReturned)
      .mockResolvedValueOnce(secondPaginatedBookingRecapReturned)

    // When
    await renderBookingsRecap(props, store)

    // Then
    expect(loadFilteredBookingsRecap).toHaveBeenCalledTimes(2)
    expect(loadFilteredBookingsRecap).toHaveBeenNthCalledWith(1, { page: 1, venueId: 'all' })
    expect(loadFilteredBookingsRecap).toHaveBeenNthCalledWith(2, { page: 2, venueId: 'all' })

    const firstBookingRecap = screen.getAllByText(bookings1.stock.offer_name)
    expect(firstBookingRecap).toHaveLength(2)
    const secondBookingRecap = screen.getAllByText(bookings2.stock.offer_name)
    expect(secondBookingRecap).toHaveLength(2)
  })
})
