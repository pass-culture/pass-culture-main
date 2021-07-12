import '@testing-library/jest-dom'
import { act, render, screen } from '@testing-library/react'
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

jest.mock('utils/date', () => ({
  ...jest.requireActual('utils/date'),
  getToday: jest.fn().mockReturnValue(new Date('2020-06-07T12:00:00Z')),
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

describe('components | BookingsRecap | Admin user', () => {
  let props
  let store
  let venue

  beforeEach(() => {
    loadFilteredBookingsRecap.mockRejectedValue({
      global: ["Le statut d'administrateur ne permet pas d'accèder au suivi des réservations"],
    })

    props = {
      location: {
        state: null,
      },
    }
    store = configureTestStore({
      data: {
        users: [{ publicName: 'René', isAdmin: true, email: 'rené@example.com' }],
      },
    })
    venue = venueFactory()
    getVenuesForOfferer.mockResolvedValue([venue])
  })

  it('should show NoBookingsMessage to an admin user and not call the API', async () => {
    // When
    await renderBookingsRecap(props, store)

    // Then
    expect(loadFilteredBookingsRecap).not.toHaveBeenCalled()
    expect(getVenuesForOfferer).not.toHaveBeenCalled()
    const bookingsTable = screen.queryByText('Télécharger le CSV')
    expect(bookingsTable).not.toBeInTheDocument()
    const noBookingsMessage = screen.getByText('Aucune réservation pour le moment')
    expect(noBookingsMessage).toBeInTheDocument()
    const spinner = screen.queryByText('Chargement en cours')
    expect(spinner).not.toBeInTheDocument()
  })
})
