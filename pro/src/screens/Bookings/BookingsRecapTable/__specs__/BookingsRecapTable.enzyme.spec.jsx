import { mount, shallow } from 'enzyme'
import React from 'react'
import { Provider } from 'react-redux'

import BookingsRecapTable from 'screens/Bookings/BookingsRecapTable/BookingsRecapTable'
import {
  TableWrapper,
  BeneficiaryCell,
  BookingDateCell,
  BookingIsDuoCell,
  BookingOfferCell,
  BookingStatusCell,
  BookingTokenCell,
  Header,
  NoFilteredBookings,
} from 'screens/Bookings/BookingsRecapTable/components'
import TablePagination from 'screens/Bookings/BookingsRecapTable/components/Table/Paginate'
import filterBookingsRecap from 'screens/Bookings/BookingsRecapTable/utils/filterBookingsRecap'
import { configureTestStore } from 'store/testUtils'
import { ReactComponent } from 'utils/svgrMock'

jest.mock(
  'screens/Bookings/BookingsRecapTable/constants/NB_BOOKINGS_PER_PAGE',
  () => ({
    NB_BOOKINGS_PER_PAGE: 1,
  })
)
jest.mock('lodash.debounce', () => jest.fn(callback => callback))
jest.mock('../utils/filterBookingsRecap', () => jest.fn())

describe('components | BookingsRecapTable', () => {
  let store

  beforeEach(() => {
    store = configureTestStore({})
  })

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
    const wrapper = mount(
      <Provider store={store}>
        <BookingsRecapTable {...props} />
      </Provider>
    )

    // Then
    const firstHeader = wrapper.find('th').at(0)
    const secondHeader = wrapper.find('th').at(1)
    const thirdHeader = wrapper.find('th').at(2)
    const fourthHeader = wrapper.find('th').at(3)
    const fifthHeader = wrapper.find('th').at(4)
    const sixthHeader = wrapper.find('th').at(5)
    expect(wrapper.find('th')).toHaveLength(6)
    expect(firstHeader.text()).toBe("Nom de l'offre")
    expect(secondHeader.text()).toBe('')
    expect(thirdHeader.text()).toBe('Bénéficiaire')
    expect(fourthHeader.text()).toBe('Réservation')
    expect(fifthHeader.text()).toBe('Contremarque')
    expect(sixthHeader.text()).toContain('Statut')
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
    const wrapper = mount(
      <Provider store={store}>
        <BookingsRecapTable {...props} />
      </Provider>
    )

    // Then
    const sixthHeader = wrapper.find('th').at(5)
    expect(sixthHeader.find('img').prop('src')).toContain(
      'ico-filter-status-black.svg'
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
    const wrapper = mount(
      <Provider store={store}>
        <BookingsRecapTable {...props} />
      </Provider>
    )

    // Then
    const bookingOfferCell = wrapper.find(BookingOfferCell)
    expect(bookingOfferCell).toHaveLength(1)
    expect(bookingOfferCell.props()).toStrictEqual({
      offer: { offer_name: 'Avez-vous déjà vu', type: 'thing' },
    })
    const duoCell = wrapper.find(BookingIsDuoCell)
    expect(duoCell.find(ReactComponent).props()).toMatchObject({
      title: 'Réservation DUO',
    })
    const beneficiaryCell = wrapper.find(BeneficiaryCell)
    expect(beneficiaryCell).toHaveLength(1)
    expect(beneficiaryCell.props()).toStrictEqual({
      beneficiaryInfos: {
        email: 'sonia.klepi@example.com',
        firstname: 'Sonia',
        lastname: 'Klepi',
      },
    })
    const bookingDateCell = wrapper.find(BookingDateCell)
    expect(bookingDateCell).toHaveLength(1)
    expect(bookingDateCell.props()).toStrictEqual({
      bookingDateTimeIsoString: '2020-04-03T12:00:00Z',
    })
    const bookingTokenCell = wrapper.find(BookingTokenCell)
    expect(bookingTokenCell).toHaveLength(1)
    expect(bookingTokenCell.props()).toStrictEqual({ bookingToken: 'ZEHBGD' })
    const bookingStatusCell = wrapper.find(BookingStatusCell)
    expect(bookingStatusCell).toHaveLength(1)
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
    const wrapper = shallow(<BookingsRecapTable {...props} />)

    // Then
    const header = wrapper.find(Header)
    expect(header).toHaveLength(1)
    expect(header.props()).toStrictEqual({
      bookingsRecapFilteredLength: bookingsRecap.length,
      isLoading: false,
    })
  })

  it('should not render a Header component when there is no filtered booking', () => {
    // given
    const bookingsRecap = []
    const props = {
      bookingsRecap: bookingsRecap,
      isLoading: false,
    }
    filterBookingsRecap.mockReturnValue(bookingsRecap)

    // When
    const wrapper = shallow(<BookingsRecapTable {...props} />)

    // Then
    const header = wrapper.find(Header)
    expect(header).toHaveLength(0)
  })

  it('should update currentPage when clicking on next page button', () => {
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
    const wrapper = mount(
      <Provider store={store}>
        <BookingsRecapTable {...props} />
      </Provider>
    )
    const paginate = wrapper.find(TablePagination)
    const nextPageButton = paginate.find('button').at(1)
    nextPageButton.simulate('click')

    // Then
    const table = wrapper.find(TableWrapper)
    expect(table.prop('nbBookingsPerPage')).toBe(1)

    const bookingOfferCell = wrapper.find(BookingOfferCell)
    expect(bookingOfferCell).toHaveLength(1)
    expect(bookingOfferCell.props()).toStrictEqual({
      offer: { offer_name: 'Avez-vous déjà vu', type: 'thing' },
    })
    const duoCell = wrapper.find(BookingIsDuoCell)
    expect(duoCell.find(ReactComponent).props()).toStrictEqual({
      title: 'Réservation DUO',
    })
    const beneficiaryCell = wrapper.find(BeneficiaryCell)
    expect(beneficiaryCell).toHaveLength(1)
    expect(beneficiaryCell.props()).toStrictEqual({
      beneficiaryInfos: {
        email: 'sonia.klepi@example.com',
        firstname: 'Sonia',
        lastname: 'Klepi',
      },
    })
    const bookingDateCell = wrapper.find(BookingDateCell)
    expect(bookingDateCell).toHaveLength(1)
    expect(bookingDateCell.props()).toStrictEqual({
      bookingDateTimeIsoString: '2020-04-03T12:00:00Z',
    })
    const bookingTokenCell = wrapper.find(BookingTokenCell)
    expect(bookingTokenCell).toHaveLength(1)
    expect(bookingTokenCell.props()).toStrictEqual({ bookingToken: 'ZEHBGD' })
    const bookingStatusCell = wrapper.find(BookingStatusCell)
    expect(bookingStatusCell).toHaveLength(1)
  })

  it('should not apply filters when component didnt receive new data', () => {
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
      },
    ]
    filterBookingsRecap.mockReturnValue(bookingsRecap)
    const props = {
      bookingsRecap: bookingsRecap,
      isLoading: false,
    }

    const wrapper = shallow(<BookingsRecapTable {...props} />)

    // When
    wrapper.setProps(props)

    // Then
    const table = wrapper.find(TableWrapper)
    expect(table.props()).toStrictEqual({
      columns: expect.any(Object),
      currentPage: 0,
      data: props.bookingsRecap,
      nbBookings: props.bookingsRecap.length,
      nbBookingsPerPage: 1,
      updateCurrentPage: expect.any(Function),
    })
  })

  it('should render a NoFilteredBookings when no bookings', () => {
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
    const wrapper = mount(
      <Provider store={store}>
        <BookingsRecapTable {...props} />
      </Provider>
    )
    const input = wrapper.find({ placeholder: "Rechercher par nom d'offre" })

    // When
    input.simulate('change', { target: { value: 'not findable' } })

    // Then
    const table = wrapper.find(TableWrapper)
    expect(table).toHaveLength(0)
    const noFilteredBookings = wrapper.find(NoFilteredBookings)
    expect(noFilteredBookings).toHaveLength(1)
    expect(noFilteredBookings.props()).toStrictEqual({
      resetFilters: expect.any(Function),
    })
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
    const wrapper = mount(
      <Provider store={store}>
        <BookingsRecapTable {...props} />
      </Provider>
    )

    const offerNameInput = wrapper.find({
      placeholder: "Rechercher par nom d'offre",
    })
    await offerNameInput.simulate('change', {
      target: { value: 'not findable' },
    })

    const noFilteredBookings = wrapper.find(NoFilteredBookings)
    const displayAllBookingsButton = noFilteredBookings.find({
      children: 'afficher toutes les réservations',
    })

    // When
    await displayAllBookingsButton.simulate('click')

    // Then
    const offerName = wrapper.find({
      placeholder: "Rechercher par nom d'offre",
    })
    expect(offerName.text()).toBe('')
  })

  // Skip is needed as this test is not compliant with a function component.
  // The setProps should re-render the bookings recap table but it doesn't.
  // We need to migrate this test to RTL.
  it.skip('should redirect to first page when applying filters', async () => {
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
    const bookingsRecap = [booking]
    filterBookingsRecap.mockReturnValueOnce(bookingsRecap).mockReturnValue([])
    const props = {
      bookingsRecap: bookingsRecap,
      isLoading: false,
    }
    const wrapper = mount(
      <Provider store={store}>
        <BookingsRecapTable {...props} />
      </Provider>
    )
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
    const paginate = wrapper.find(TablePagination)
    const nextPageButton = paginate.find('button').at(1)
    nextPageButton.simulate('click')

    // when
    await wrapper.setProps({
      bookingsRecap: bookingsRecap.concat([newBooking]),
    })

    // then
    const table = wrapper.find(TableWrapper)
    expect(table.prop('currentPage')).toBe(0)
  })
})
