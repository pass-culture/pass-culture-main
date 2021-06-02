import '@testing-library/jest-dom'
import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import * as bookingRecapsService from 'repository/bookingsRecapService'
import { fetchAllVenuesByProUser } from 'repository/venuesService'
import { venueFactory } from 'utils/apiFactories'

import { configureTestStore } from '../../../../store/testUtils'
import BookingsRecapContainer from '../BookingsRecapContainer'

jest.mock('repository/venuesService', () => ({
  ...jest.requireActual('repository/venuesService'),
  fetchAllVenuesByProUser: jest.fn(),
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
  let fetchBookingsRecapByPageStub
  let fetchBookingsRecapByPageSpy
  let props
  let store
  let venue

  beforeEach(() => {
    fetchBookingsRecapByPageStub = Promise.resolve({
      bookings_recap: [],
      page: 0,
      pages: 0,
      total: 0,
    })
    fetchBookingsRecapByPageSpy = jest
      .spyOn(bookingRecapsService, 'fetchBookingsRecapByPage')
      .mockImplementation(() => fetchBookingsRecapByPageStub)
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
    fetchAllVenuesByProUser.mockResolvedValue([venue])
  })

  it('should show a pre-filter section', async () => {
    // When
    await renderBookingsRecap(props, store)

    // Then
    const eventDateFilter = screen.getByText('Date de l’évènement', { selector: 'label' })
    const eventVenueFilter = screen.getByText('Lieu', { selector: 'label' })
    const eventBookingPeriodFilter = screen.getByText('Période de réservation', {
      selector: 'label',
    })
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
    expect(fetchBookingsRecapByPageSpy).toHaveBeenCalledWith(1, { venueId: venue.id })
  })
})
