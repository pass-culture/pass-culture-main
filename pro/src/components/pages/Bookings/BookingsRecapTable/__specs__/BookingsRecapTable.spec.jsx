import '@testing-library/jest-dom'

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'

import { configureTestStore } from 'store/testUtils'

import BookingsRecapTable from '../BookingsRecapTable'

describe('components | BookingsRecapTable', () => {
  let store

  beforeEach(() => {
    store = configureTestStore({})
  })

  it('should filter when filters change', async () => {
    const bookingsRecap = [
      {
        stock: {
          offer_name: 'Avez-vous déjà vu',
          type: 'thing',
        },
        beneficiary: {
          lastname: 'Klepi',
          firstname: 'Sonia',
          email: 'sonia.klepi@example.com',
        },
        booking_amount: 10,
        booking_date: '2020-04-03T12:00:00Z',
        booking_token: 'ZEHBGD',
        booking_status: 'validated',
        booking_is_duo: true,
        venue: {
          identifier: 'AE',
          name: 'Librairie Kléber',
        },
        booking_status_history: [
          {
            status: 'booked',
            date: '2020-04-03T12:00:00Z',
          },
          {
            status: 'validated',
            date: '2020-04-23T12:00:00Z',
          },
        ],
      },
      {
        stock: {
          offer_name: 'Autre nom offre',
          type: 'thing',
        },
        beneficiary: {
          lastname: 'Parjeot',
          firstname: 'Micheline',
          email: 'michelinedu72@example.com',
        },
        booking_amount: 10,
        booking_date: '2020-04-03T12:00:00Z',
        booking_token: 'ABCDE',
        booking_status: 'validated',
        booking_is_duo: true,
        venue: {
          identifier: 'AE',
          name: 'Librairie Kléber',
        },
        booking_status_history: [
          {
            status: 'booked',
            date: '2020-04-03T12:00:00Z',
          },
          {
            status: 'validated',
            date: '2020-05-06T12:00:00Z',
          },
        ],
      },
    ]
    const props = {
      bookingsRecap: bookingsRecap,
      isLoading: false,
    }
    render(
      <Provider store={store}>
        <BookingsRecapTable {...props} />
      </Provider>
    )

    // 2 lines = 12 cells
    expect(screen.getAllByRole('cell')).toHaveLength(12)

    userEvent.type(screen.getByRole('textbox'), 'Autre nom offre')
    await waitFor(() => {
      // 1 line = 6 cells
      expect(screen.getAllByRole('cell')).toHaveLength(6)
    })

    userEvent.selectOptions(
      screen.getByRole('combobox'),
      screen.getByRole('option', { name: 'Bénéficiaire' })
    )
    userEvent.clear(screen.getByRole('textbox'))

    await waitFor(() => {
      // 2 lines = 12 cells
      expect(screen.getAllByRole('cell')).toHaveLength(12)
    })
    userEvent.type(screen.getByRole('textbox'), 'Parjeot')
    await waitFor(() => {
      // 1 line = 6 cells
      expect(screen.getAllByRole('cell')).toHaveLength(6)
    })
  })
})
