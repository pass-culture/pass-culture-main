import '@testing-library/jest-dom'
import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { getVenuesForOfferer, loadFilteredBookingsRecap } from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'
import { venueFactory } from 'utils/apiFactories'

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
})
