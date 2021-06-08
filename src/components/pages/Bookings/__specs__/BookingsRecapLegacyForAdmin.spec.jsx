import '@testing-library/jest-dom'
import { act, render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { loadFilteredBookingsRecap } from '../../../../repository/pcapi/pcapi'
import { configureTestStore } from '../../../../store/testUtils'
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
        users: [{ publicName: 'René', isAdmin: true, email: 'rené@example.com' }],
      },
    })
  })

  it('should show NoBookingsMessage to an admin user', async () => {
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
})
