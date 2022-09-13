import '@testing-library/jest-dom'
import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'

import BookingsRecapTable from 'screens/Bookings/BookingsRecapTable/BookingsRecapTable'
import filterBookingsRecap from 'screens/Bookings/BookingsRecapTable/utils/filterBookingsRecap'
import { configureTestStore } from 'store/testUtils'

jest.mock(
  'screens/Bookings/BookingsRecapTable/constants/NB_BOOKINGS_PER_PAGE',
  () => ({
    NB_BOOKINGS_PER_PAGE: 1,
  })
)
jest.mock('lodash.debounce', () => jest.fn(callback => callback))
jest.mock('../utils/filterBookingsRecap', () => jest.fn())

describe('components | BookingsRecapTable', () => {
  const renderBookingRecap = props => {
    return render(
      <Provider store={configureTestStore({})}>
        <BookingsRecapTable {...props} />
      </Provider>
    )
  }

  it('should render the expected table headers', () => {
    // Given
    const props = {
      bookingsRecap: [
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
              date: '2020-05-12T12:00:00Z',
            },
          ],
        },
      ],
      isLoading: false,
    }
    filterBookingsRecap.mockReturnValue(props.bookingsRecap)

    // When
    renderBookingRecap(props)

    // Then
    const headers = screen.getAllByRole('columnheader')
    expect(headers).toHaveLength(6)
    expect(headers[0]).toHaveTextContent("Nom de l'offre")
    expect(headers[1]).toHaveTextContent('')
    expect(headers[2]).toHaveTextContent('Bénéficiaire')
    expect(headers[3]).toHaveTextContent('Réservation')
    expect(headers[4]).toHaveTextContent('Contremarque')
    expect(headers[5]).toHaveTextContent('Statut')
  })

  it('should render a filter icon in "statut" header', () => {
    // Given
    const props = {
      bookingsRecap: [
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
              date: '2020-05-12T12:00:00Z',
            },
          ],
        },
      ],
      isLoading: false,
    }
    filterBookingsRecap.mockReturnValue(props.bookingsRecap)

    // When
    renderBookingRecap(props)

    // Then
    const header = screen.getAllByRole('columnheader')[5]
    expect(within(header).getByRole('img')).toHaveAttribute(
      'src',
      expect.stringContaining('ico-filter-status-black.svg')
    )
  })

  it('should render the expected table rows', () => {
    // Given
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
            date: '2020-04-13T12:00:00Z',
          },
        ],
      },
    ]
    filterBookingsRecap.mockReturnValue(bookingsRecap)

    const props = {
      bookingsRecap: bookingsRecap,
      isLoading: false,
    }

    // When
    renderBookingRecap(props)

    // Then
    const bookingRow = screen.getAllByRole('cell')

    expect(bookingRow[0]).toHaveTextContent('Avez-vous déjà vu')
    expect(bookingRow[1].querySelector('div')).toHaveAttribute(
      'title',
      'Réservation DUO'
    )
    expect(bookingRow[2]).toHaveTextContent('Klepi Sonia')
    expect(bookingRow[3]).toHaveTextContent('03/04/202012:00')
    expect(bookingRow[4]).toHaveTextContent('ZEHBGD')
    expect(bookingRow[5]).toHaveTextContent('validé')
  })

  it('should render a Header component when there is at least one filtered booking', () => {
    // given
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
        booking_is_duo: false,
        venue_identifier: 'AE',
        booking_status_history: [
          {
            status: 'booked',
            date: '2020-04-03T12:00:00Z',
          },
          {
            status: 'validated',
            date: '2020-06-01T12:00:00Z',
          },
        ],
      },
    ]
    filterBookingsRecap.mockReturnValue(bookingsRecap)
    const props = {
      bookingsRecap: bookingsRecap,
      isLoading: false,
    }

    // When
    renderBookingRecap(props)

    // Then
    expect(screen.getByText('1 réservation')).toBeInTheDocument()
  })

  it('should not render a Header component when there is no filtered booking', async () => {
    // given
    const bookingsRecap = []
    const props = {
      bookingsRecap: bookingsRecap,
      isLoading: false,
    }
    filterBookingsRecap.mockReturnValue(bookingsRecap)

    // When
    renderBookingRecap(props)

    // Then
    expect(await screen.queryByRole('row')).not.toBeInTheDocument()
  })

  it('should update currentPage when clicking on next page button', async () => {
    // Given
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
            date: '2020-05-06T12:00:00Z',
          },
        ],
      },
    ]
    filterBookingsRecap.mockReturnValue(bookingsRecap)

    const props = {
      bookingsRecap: bookingsRecap,
      isLoading: false,
    }

    // When
    renderBookingRecap(props)
    await userEvent.click(screen.getAllByRole('button')[1])

    // Then
    const bookingRow = screen.getAllByRole('cell')

    expect(bookingRow[0]).toHaveTextContent('Avez-vous déjà vu')
    expect(bookingRow[1].querySelector('div')).toHaveAttribute(
      'title',
      'Réservation DUO'
    )
    expect(bookingRow[2]).toHaveTextContent('Klepi Sonia')
    expect(bookingRow[3]).toHaveTextContent('03/04/202012:00')
    expect(bookingRow[4]).toHaveTextContent('ZEHBGD')
    expect(bookingRow[5]).toHaveTextContent('validé')
  })

  it('should render a NoFilteredBookings when no bookings', async () => {
    // given
    filterBookingsRecap.mockReturnValue([])
    const booking = {
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
      booking_is_duo: false,
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
          date: '2020-04-14T12:00:00Z',
        },
      ],
    }
    const props = {
      bookingsRecap: [booking],
      isLoading: false,
    }

    renderBookingRecap(props)

    const input = screen.getByPlaceholderText("Rechercher par nom d'offre")

    // When
    await userEvent.type(input, 'not findable')
    // Then
    expect(
      screen.getByText('Aucune réservation trouvée pour votre recherche')
    ).toBeInTheDocument()
  })

  it('should reset filters when clicking on "afficher toutes les réservations"', async () => {
    // given
    const props = {
      bookingsRecap: [
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
          booking_is_duo: false,
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
              date: '2020-04-16T12:00:00Z',
            },
          ],
        },
      ],
      isLoading: false,
    }
    filterBookingsRecap.mockReturnValue([])
    renderBookingRecap(props)

    const input = screen.getByPlaceholderText("Rechercher par nom d'offre")

    await userEvent.type(input, 'not findable')

    const displayAllBookingsButton = screen.getByRole('button', {
      text: 'afficher toutes les réservations',
    })

    // When
    await userEvent.click(displayAllBookingsButton)

    // Then
    const offerName = screen.getByPlaceholderText("Rechercher par nom d'offre")
    expect(offerName).toHaveValue('')
  })

  it('should redirect to first page when applying filters', async () => {
    // given
    const booking = {
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
          date: '2020-04-16T12:00:00Z',
        },
      ],
    }
    const newBooking = {
      stock: {
        offer_name: 'Jurassic Park',
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
      venue_identifier: 'AE',
      booking_status_history: [
        {
          status: 'booked',
          date: '2020-04-03T12:00:00Z',
        },
        {
          status: 'validated',
          date: '2020-04-16T12:00:00Z',
        },
      ],
    }
    const bookingsRecap = [booking]
    filterBookingsRecap
      .mockReturnValueOnce(bookingsRecap)
      .mockReturnValue([newBooking])
    const props = {
      bookingsRecap: bookingsRecap,
      isLoading: false,
    }
    renderBookingRecap(props)

    await userEvent.click(screen.getAllByRole('button')[1])

    // when
    const input = screen.getByPlaceholderText("Rechercher par nom d'offre")

    await userEvent.type(input, 'not findable')

    // then
    expect(screen.getByText('Page 1/1')).toBeInTheDocument()
  })
})
