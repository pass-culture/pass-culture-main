import '@testing-library/jest-dom'

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import type { Store } from 'redux'

import {
  BookingRecapStatus,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'
import { Audience } from 'core/shared'
import { EMPTY_FILTER_VALUE } from 'screens/Bookings/BookingsRecapTable/components/Filters/_constants'
import * as constants from 'screens/Bookings/BookingsRecapTable/constants/NB_BOOKINGS_PER_PAGE'
import * as filterBookingsRecap from 'screens/Bookings/BookingsRecapTable/utils/filterBookingsRecap'
import { RootState } from 'store/reducers'
import { configureTestStore } from 'store/testUtils'

import BookingsRecapTable from '../BookingsRecapTable'

const mockedBooking = {
  stock: {
    offer_name: 'Avez-vous déjà vu',
    type: 'thing',
    stock_identifier: '1',
    offer_identifier: '1',
    offer_is_educational: false,
  },
  beneficiary: {
    lastname: 'Klepi',
    firstname: 'Sonia',
    email: 'sonia.klepi@example.com',
  },
  booking_amount: 10,
  booking_date: '2020-04-03T12:00:00Z',
  booking_token: 'ZEHBGD',
  booking_status: BookingRecapStatus.VALIDATED,
  booking_is_duo: true,
  venue: {
    identifier: 'AE',
    name: 'Librairie Kléber',
  },
  booking_status_history: [
    {
      status: BookingRecapStatus.BOOKED,
      date: '2020-04-03T12:00:00Z',
    },
    {
      status: BookingRecapStatus.VALIDATED,
      date: '2020-04-23T12:00:00Z',
    },
  ],
}

const otherBooking = {
  stock: {
    offer_name: 'Autre nom offre',
    type: 'thing',
    stock_identifier: '2',
    offer_identifier: '2',
    offer_is_educational: false,
  },
  beneficiary: {
    lastname: 'Parjeot',
    firstname: 'Micheline',
    email: 'michelinedu72@example.com',
  },
  booking_amount: 10,
  booking_date: '2020-04-03T12:00:00Z',
  booking_token: 'ABCDE',
  booking_status: BookingRecapStatus.VALIDATED,
  booking_is_duo: true,
  venue: {
    identifier: 'AE',
    name: 'Librairie Kléber',
  },
  booking_status_history: [
    {
      status: BookingRecapStatus.BOOKED,
      date: '2020-04-03T12:00:00Z',
    },
    {
      status: BookingRecapStatus.VALIDATED,
      date: '2020-05-06T12:00:00Z',
    },
  ],
}

const collectiveBookingsRecap: CollectiveBookingResponseModel[] = [
  {
    stock: {
      offer_name: 'Autre nom offre',
      offer_identifier: '2',
      offer_is_educational: false,
      event_beginning_datetime: '2020-04-13T12:00:00Z',
      number_of_tickets: 10,
    },
    institution: {
      id: 1,
      institutionType: 'COLLEGE',
      name: 'BELLEVUE',
      postalCode: '30100',
      city: 'Ales',
      phoneNumber: '',
    },
    booking_identifier: 'A1',
    booking_amount: 10,
    booking_date: '2020-04-03T12:00:00Z',
    booking_token: 'ABCDE',
    booking_status: BookingRecapStatus.VALIDATED,
    booking_is_duo: true,
    booking_status_history: [
      {
        status: BookingRecapStatus.BOOKED,
        date: '2020-04-03T12:00:00Z',
      },
      {
        status: BookingRecapStatus.VALIDATED,
        date: '2020-05-06T12:00:00Z',
      },
    ],
  },
]

describe('components | BookingsRecapTable', () => {
  let store: Store<Partial<RootState>>

  beforeEach(() => {
    store = configureTestStore({})
  })

  it('should filter when filters change', async () => {
    const bookingsRecap = [mockedBooking, otherBooking]
    const props = {
      bookingsRecap: bookingsRecap,
      isLoading: false,
      audience: Audience.INDIVIDUAL,
      reloadBookings: jest.fn(),
    }
    render(
      <Provider store={store}>
        <BookingsRecapTable {...props} />
      </Provider>
    )

    // 2 lines = 12 cells
    expect(screen.getAllByRole('cell')).toHaveLength(12)

    await userEvent.type(screen.getByRole('textbox'), 'Autre nom offre')
    await waitFor(() => {
      // 1 line = 6 cells
      expect(screen.getAllByRole('cell')).toHaveLength(6)
    })

    await userEvent.selectOptions(
      screen.getByRole('combobox'),
      screen.getByRole('option', { name: 'Bénéficiaire' })
    )
    await userEvent.clear(screen.getByRole('textbox'))

    await waitFor(() => {
      // 2 lines = 12 cells
      expect(screen.getAllByRole('cell')).toHaveLength(12)
    })
    await userEvent.type(screen.getByRole('textbox'), 'Parjeot')
    await waitFor(() => {
      // 1 line = 6 cells
      expect(screen.getAllByRole('cell')).toHaveLength(6)
    })
  })

  it('should filter bookings on render', () => {
    jest.mock('../utils/filterBookingsRecap', () => jest.fn())

    // Given
    const props = {
      bookingsRecap: [mockedBooking],
      isLoading: false,
      locationState: {
        statuses: ['booked', 'cancelled'],
      },
      audience: Audience.INDIVIDUAL,
      reloadBookings: jest.fn(),
    }
    jest.spyOn(filterBookingsRecap, 'default').mockReturnValue([])

    // When
    render(
      <Provider store={store}>
        <BookingsRecapTable {...props} />
      </Provider>
    )

    // Then
    expect(filterBookingsRecap.default).toHaveBeenCalledWith(
      props.bookingsRecap,
      expect.objectContaining({
        bookingStatus: props.locationState.statuses,
        bookingBeneficiary: EMPTY_FILTER_VALUE,
        bookingToken: EMPTY_FILTER_VALUE,
        offerISBN: EMPTY_FILTER_VALUE,
        offerName: EMPTY_FILTER_VALUE,
      })
    )
  })

  it('should render the expected table with max given number of hits per page', () => {
    // Given
    // @ts-ignore
    // eslint-disable-next-line
    constants.NB_BOOKINGS_PER_PAGE = 1
    const bookingsRecap = [mockedBooking, otherBooking]
    jest.spyOn(filterBookingsRecap, 'default').mockReturnValue(bookingsRecap)
    const props = {
      bookingsRecap: bookingsRecap,
      isLoading: false,
      audience: Audience.INDIVIDUAL,
      reloadBookings: jest.fn(),
    }

    // When
    render(
      <Provider store={store}>
        <BookingsRecapTable {...props} />
      </Provider>
    )

    // Then
    // 1 line = 6 cells
    const cells = screen.getAllByRole('columnheader')
    expect(cells).toHaveLength(6)
    expect(cells[0]).toHaveTextContent("Nom de l'offre")
    expect(cells[1]).toHaveTextContent('')
    expect(cells[2]).toHaveTextContent('Bénéficiaire')
    expect(cells[3]).toHaveTextContent('Réservation')
    expect(cells[4]).toHaveTextContent('Contremarque')
    expect(cells[5]).toHaveTextContent('Statut')
  })

  it('should render the expected table for collective audience', () => {
    // Given
    // @ts-ignore
    // eslint-disable-next-line
    constants.NB_BOOKINGS_PER_PAGE = 1
    jest
      .spyOn(filterBookingsRecap, 'default')
      .mockReturnValue(collectiveBookingsRecap)
    const props = {
      bookingsRecap: collectiveBookingsRecap,
      isLoading: false,
      audience: Audience.COLLECTIVE,
      reloadBookings: jest.fn(),
    }

    // When
    render(
      <Provider store={store}>
        <BookingsRecapTable {...props} />
      </Provider>
    )

    // Then
    // 1 line = 6 cells
    const cells = screen.getAllByRole('columnheader')
    expect(cells).toHaveLength(5)
    expect(cells[0]).toHaveTextContent("Nom de l'offre")
    expect(cells[1]).toHaveTextContent('Établissement')
    expect(cells[2]).toHaveTextContent('Places et prix')
    expect(cells[3]).toHaveTextContent('Statut')
    expect(cells[4]).toHaveTextContent('')
  })
})
