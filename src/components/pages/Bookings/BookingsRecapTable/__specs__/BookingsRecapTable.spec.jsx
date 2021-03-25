import { mount, shallow } from 'enzyme'
import React from 'react'
import DatePicker from 'react-datepicker'

import { ReactComponent } from 'utils/svgrMock'

import BookingsRecapTable from '../BookingsRecapTable'
import BeneficiaryCell from '../CellsFormatter/BeneficiaryCell'
import BookingDateCell from '../CellsFormatter/BookingDateCell'
import BookingIsDuoCell from '../CellsFormatter/BookingIsDuoCell'
import BookingOfferCell from '../CellsFormatter/BookingOfferCell'
import BookingStatusCell from '../CellsFormatter/BookingStatusCell'
import BookingTokenCell from '../CellsFormatter/BookingTokenCell'
import { ALL_BOOKING_STATUS, ALL_VENUES, EMPTY_FILTER_VALUE } from '../Filters/_constants'
import Filters from '../Filters/Filters'
import Header from '../Header/Header'
import { NB_BOOKINGS_PER_PAGE } from '../NB_BOOKINGS_PER_PAGE'
import NoFilteredBookings from '../NoFilteredBookings/NoFilteredBookings'
import TablePagination from '../Table/Paginate/TablePagination'
import TableFrame from '../Table/TableFrame'
import filterBookingsRecap from '../utils/filterBookingsRecap'

jest.mock('../NB_BOOKINGS_PER_PAGE', () => ({
  NB_BOOKINGS_PER_PAGE: 1,
}))
jest.mock('lodash.debounce', () => jest.fn(callback => callback))
jest.mock('../utils/filterBookingsRecap', () => jest.fn())

describe('components | BookingsRecapTable', () => {
  it('should render a TableContainer component with columns and data props', () => {
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
            date: '2020-05-03T12:00:00Z',
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
        booking_date: '2020-04-03T12:00:00Z',
        booking_token: 'ZEHBGD',
        booking_status: 'validated',
        booking_is_duo: true,
        venue_identifier: 'AF',
        booking_status_history: [
          {
            status: 'booked',
            date: '2020-04-03T12:00:00Z',
          },
          {
            status: 'validated',
            date: '2020-05-03T12:00:00Z',
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
    const table = wrapper.find(TableFrame)

    // Then
    expect(table).toHaveLength(1)
    expect(table.props()).toStrictEqual({
      columns: wrapper.state('columns'),
      data: bookingsRecap,
      nbBookings: 2,
      nbBookingsPerPage: NB_BOOKINGS_PER_PAGE,
      currentPage: 0,
      updateCurrentPage: expect.any(Function),
    })
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
    const wrapper = mount(<BookingsRecapTable {...props} />)

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
    const wrapper = mount(<BookingsRecapTable {...props} />)

    // Then
    const sixthHeader = wrapper.find('th').at(5)
    expect(sixthHeader.find('img').prop('src')).toContain('ico-filter-status-black.svg')
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
    const wrapper = mount(<BookingsRecapTable {...props} />)

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
      beneficiaryInfos: { email: 'sonia.klepi@example.com', firstname: 'Sonia', lastname: 'Klepi' },
    })
    const bookingDateCell = wrapper.find(BookingDateCell)
    expect(bookingDateCell).toHaveLength(1)
    expect(bookingDateCell.props()).toStrictEqual({ bookingDate: '2020-04-03T12:00:00Z' })
    const bookingTokenCell = wrapper.find(BookingTokenCell)
    expect(bookingTokenCell).toHaveLength(1)
    expect(bookingTokenCell.props()).toStrictEqual({ bookingToken: 'ZEHBGD' })
    const bookingStatusCell = wrapper.find(BookingStatusCell)
    expect(bookingStatusCell).toHaveLength(1)
  })

  it('should render the expected table with max given number of hits per page', () => {
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
        booking_date: '2020-04-03T12:00:00Z',
        booking_is_duo: false,
        booking_token: 'ZEHBGD',
        booking_status: 'validated',
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
            date: '2020-05-01T12:00:00Z',
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
    const wrapper = mount(<BookingsRecapTable {...props} />)

    // Then
    const table = wrapper.find(TableFrame)
    expect(table).toHaveLength(1)
    expect(table.props()).toStrictEqual({
      columns: wrapper.state('columns'),
      data: bookingsRecap,
      nbBookings: 1,
      nbBookingsPerPage: NB_BOOKINGS_PER_PAGE,
      currentPage: 0,
      updateCurrentPage: expect.any(Function),
    })
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
      bookingsRecapFiltered: bookingsRecap,
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
    const wrapper = mount(<BookingsRecapTable {...props} />)
    const paginate = wrapper.find(TablePagination)
    const nextPageButton = paginate.find('button').at(1)
    nextPageButton.simulate('click')

    // Then
    const table = wrapper.find(TableFrame)
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
      beneficiaryInfos: { email: 'sonia.klepi@example.com', firstname: 'Sonia', lastname: 'Klepi' },
    })
    const bookingDateCell = wrapper.find(BookingDateCell)
    expect(bookingDateCell).toHaveLength(1)
    expect(bookingDateCell.props()).toStrictEqual({ bookingDate: '2020-04-03T12:00:00Z' })
    const bookingTokenCell = wrapper.find(BookingTokenCell)
    expect(bookingTokenCell).toHaveLength(1)
    expect(bookingTokenCell.props()).toStrictEqual({ bookingToken: 'ZEHBGD' })
    const bookingStatusCell = wrapper.find(BookingStatusCell)
    expect(bookingStatusCell).toHaveLength(1)
  })

  it('should render filters component with expected props', () => {
    // given
    const bookingsRecap = []
    const props = {
      bookingsRecap: bookingsRecap,
      isLoading: true,
    }
    filterBookingsRecap.mockReturnValueOnce(bookingsRecap)

    // When
    const wrapper = shallow(<BookingsRecapTable {...props} />)

    // Then
    const filters = wrapper.find(Filters)
    expect(filters.props()).toStrictEqual({
      isLoading: true,
      oldestBookingDate: '',
      updateGlobalFilters: expect.any(Function),
      offerVenue: 'all',
    })
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
    const table = wrapper.find(TableFrame)
    expect(table.props()).toStrictEqual({
      columns: expect.any(Object),
      currentPage: 0,
      data: props.bookingsRecap,
      nbBookings: props.bookingsRecap.length,
      nbBookingsPerPage: 1,
      updateCurrentPage: expect.any(Function),
    })
  })

  it('should apply filters when component received new data', () => {
    // given
    filterBookingsRecap.mockReturnValue([
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
        booking_date: '2020-04-03T12:00:00Z',
        booking_token: 'ZEHBGD',
        booking_status: 'validated',
        booking_is_duo: false,
        venue_identifier: 'AE',
      },
    ])
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
      booking_date: '2020-04-03T12:00:00Z',
      booking_token: 'ZEHBGD',
      booking_status: 'validated',
      booking_is_duo: false,
      venue_identifier: 'AE',
    }
    const bookingsRecap = [booking]
    const newBooking = {
      stock: {
        offer_name: 'Merlin enchanteur',
        type: 'thing',
      },
      beneficiary: {
        lastname: 'Klepi',
        firstname: 'Sonia',
        email: 'sonia.klepi@example.com',
      },
      booking_date: '2020-04-03T12:00:00Z',
      booking_token: 'ZEHBGD',
      booking_status: 'validated',
      booking_is_duo: false,
      venue_identifier: 'AE',
    }
    const props = {
      bookingsRecap: bookingsRecap,
      isLoading: false,
    }
    const wrapper = shallow(<BookingsRecapTable {...props} />)

    // When
    wrapper.setState({ filters: { offerName: 'Avez', offerDate: null, offerVenue: ALL_VENUES } })
    const expectedBookingsRecap = [...props.bookingsRecap].concat([newBooking])
    wrapper.setProps({
      bookingsRecap: expectedBookingsRecap,
    })

    // Then
    const table = wrapper.find(TableFrame)
    expect(table.props()).toStrictEqual({
      columns: expect.any(Object),
      currentPage: 0,
      data: [booking],
      nbBookings: 1,
      nbBookingsPerPage: 1,
      updateCurrentPage: expect.any(Function),
    })
    expect(filterBookingsRecap).toHaveBeenCalledWith(expectedBookingsRecap, {
      offerName: 'Avez',
      offerDate: null,
      offerVenue: ALL_VENUES,
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
    const wrapper = mount(<BookingsRecapTable {...props} />)
    const input = wrapper.find(Filters).find({ placeholder: "Rechercher par nom d'offre" })

    // When
    input.simulate('change', { target: { value: 'not findable' } })

    // Then
    const table = wrapper.find(TableFrame)
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
    const wrapper = mount(<BookingsRecapTable {...props} />)

    const offerNameInput = wrapper.find(Filters).find({ placeholder: "Rechercher par nom d'offre" })
    await offerNameInput.simulate('change', { target: { value: 'not findable' } })

    const selectedDate = new Date('2020-05-20')
    const offerDatePicker = wrapper.find(Filters).find(DatePicker).at(0)
    await offerDatePicker.simulate('change', selectedDate)

    const noFilteredBookings = wrapper.find(NoFilteredBookings)
    const displayAllBookingsButton = noFilteredBookings.find({
      children: 'afficher toutes les réservations',
    })

    // When
    await displayAllBookingsButton.simulate('click')

    // Then
    const offerName = wrapper.find(Filters).find({ placeholder: "Rechercher par nom d'offre" })
    expect(offerName.text()).toBe('')
    const offerDate = wrapper.find(Filters).find(DatePicker).at(0)
    expect(offerDate.prop('selected')).toBe(EMPTY_FILTER_VALUE)
  })

  it('should apply default filters when mounting component with bookings', () => {
    // Given
    const props = {
      bookingsRecap: [],
      isLoading: true,
    }
    filterBookingsRecap.mockReturnValue([
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
            date: '2020-04-16T12:00:00Z',
          },
        ],
      },
    ])
    const wrapper = shallow(<BookingsRecapTable {...props} />)
    const updatedProps = {
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
              date: '2020-04-16T12:00:00Z',
            },
          ],
        },
      ],
    }

    // When
    wrapper.setProps(updatedProps)

    // Then
    expect(filterBookingsRecap).toHaveBeenCalledWith(updatedProps.bookingsRecap, {
      bookingBeginningDate: EMPTY_FILTER_VALUE,
      bookingBeneficiary: EMPTY_FILTER_VALUE,
      bookingEndingDate: EMPTY_FILTER_VALUE,
      bookingStatus: ALL_BOOKING_STATUS,
      bookingToken: EMPTY_FILTER_VALUE,
      offerDate: EMPTY_FILTER_VALUE,
      offerISBN: EMPTY_FILTER_VALUE,
      offerName: EMPTY_FILTER_VALUE,
      offerVenue: ALL_VENUES,
    })
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
    const wrapper = mount(<BookingsRecapTable {...props} />)
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
    const table = wrapper.find(TableFrame)
    expect(table.prop('currentPage')).toStrictEqual(0)
  })

  it('should filter bookings on render', () => {
    // Given
    const props = {
      bookingsRecap: [
        {
          stock: {
            offer_name: 'Avez-vous déjà vu ?',
            type: 'thing',
          },
          beneficiary: {
            lastname: 'Klepi',
            firstname: 'Sonia',
            email: 'sonia.klepi@example.com',
          },
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
      locationState: {
        venueId: 'BD',
        statuses: ['booked', 'cancelled'],
      },
    }
    filterBookingsRecap.mockReturnValue([])

    // When
    shallow(<BookingsRecapTable {...props} />)

    // Then
    expect(filterBookingsRecap).toHaveBeenCalledWith(props.bookingsRecap, {
      offerVenue: props.locationState.venueId,
      bookingStatus: props.locationState.statuses,
      bookingBeneficiary: EMPTY_FILTER_VALUE,
      bookingBeginningDate: EMPTY_FILTER_VALUE,
      bookingEndingDate: EMPTY_FILTER_VALUE,
      bookingToken: EMPTY_FILTER_VALUE,
      offerDate: EMPTY_FILTER_VALUE,
      offerISBN: EMPTY_FILTER_VALUE,
      offerName: EMPTY_FILTER_VALUE,
    })
  })
})
