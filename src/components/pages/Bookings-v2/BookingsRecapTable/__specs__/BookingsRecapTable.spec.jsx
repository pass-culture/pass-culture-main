import BookingsRecapTable from '../BookingsRecapTable'
import TableFrame from '../Table/TableFrame'
import React from 'react'
import { mount, shallow } from 'enzyme'
import BookingIsDuoCell from '../CellsFormatter/BookingIsDuoCell'
import BeneficiaryCell from '../CellsFormatter/BeneficiaryCell'
import BookingDateCell from '../CellsFormatter/BookingDateCell'
import BookingTokenCell from '../CellsFormatter/BookingTokenCell'
import BookingStatusCell from '../CellsFormatter/BookingStatusCell'
import BookingOfferCell from '../CellsFormatter/BookingOfferCell'
import Header from '../Header/Header'
import Paginate from '../Table/Paginate/Paginate'
import { NB_BOOKINGS_PER_PAGE } from '../NB_BOOKINGS_PER_PAGE'
import NoFilteredBookings from '../NoFilteredBookings/NoFilteredBookings'
import Filters from '../Filters/Filters'
import filterBookingsRecap from '../utils/filterBookingsRecap'
import DatePicker from 'react-datepicker'
import moment from 'moment'

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
        },
        beneficiary: {
          lastname: 'Klepi',
          firstname: 'Sonia',
          email: 'sonia.klepi@example.com',
        },
        booking_date: '2020-04-03T12:00:00Z',
        booking_token: 'ZEHBGD',
        booking_status: 'Validé',
        booking_is_duo: false,
      },
      {
        stock: {
          offer_name: 'Avez-vous déjà vu',
        },
        beneficiary: {
          lastname: 'Klepi',
          firstname: 'Sonia',
          email: 'sonia.klepi@example.com',
        },
        booking_date: '2020-04-03T12:00:00Z',
        booking_token: 'ZEHBGD',
        booking_status: 'Validé',
        booking_is_duo: true,
      },
    ]

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
          },
          beneficiary: {
            lastname: 'Klepi',
            firstname: 'Sonia',
            email: 'sonia.klepi@example.com',
          },
          booking_date: '2020-04-03T12:00:00Z',
          booking_token: 'ZEHBGD',
          booking_status: 'Validé',
          booking_is_duo: true,
        },
      ],
      isLoading: false,
    }

    // When
    const wrapper = mount(<BookingsRecapTable {...props} />)
    const firstHeader = wrapper.find('th').at(0)
    const secondHeader = wrapper.find('th').at(1)
    const thirdHeader = wrapper.find('th').at(2)
    const fourthHeader = wrapper.find('th').at(3)
    const fifthHeader = wrapper.find('th').at(4)
    const sixthHeader = wrapper.find('th').at(5)

    // Then
    expect(wrapper.find('th')).toHaveLength(6)
    expect(firstHeader.text()).toBe('Nom de l\'offre')
    expect(secondHeader.text()).toBe('')
    expect(thirdHeader.text()).toBe('Bénéficiaire')
    expect(fourthHeader.text()).toBe('Réservation')
    expect(fifthHeader.text()).toBe('Contremarque')
    expect(sixthHeader.text()).toBe('Statut')
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
        booking_status: 'Validé',
        booking_is_duo: true,
      },
    ]

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
    expect(duoCell.find('Icon').props()).toMatchObject({
      alt: 'Réservation DUO',
      svg: 'ico-duo',
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
    expect(bookingStatusCell.props()).toStrictEqual({ bookingStatus: 'Validé' })
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
        booking_status: 'Validé',
      },
    ]
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

  it('should render a Header component', () => {
    // given
    const bookingsRecap = [
      {
        stock: {
          offer_name: 'Avez-vous déjà vu',
        },
        beneficiary: {
          lastname: 'Klepi',
          firstname: 'Sonia',
          email: 'sonia.klepi@example.com',
        },
        booking_date: '2020-04-03T12:00:00Z',
        booking_token: 'ZEHBGD',
        booking_status: 'Validé',
      },
    ]
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
      isLoading: false,
      nbBookings: 1,
    })
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
        booking_status: 'Validé',
        booking_is_duo: true,
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
        booking_status: 'Validé',
        booking_is_duo: true,
      },
    ]

    const props = {
      bookingsRecap: bookingsRecap,
      isLoading: false,
    }

    // When
    const wrapper = mount(<BookingsRecapTable {...props} />)
    const paginate = wrapper.find(Paginate)
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
    expect(duoCell.find('Icon').props()).toMatchObject({
      alt: 'Réservation DUO',
      svg: 'ico-duo',
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
    expect(bookingStatusCell.props()).toStrictEqual({ bookingStatus: 'Validé' })
  })

  it('should not apply filters when component didnt receive new data', () => {
    // given
    const bookingsRecap = [
      {
        stock: {
          offer_name: 'Avez-vous déjà vu',
        },
        beneficiary: {
          lastname: 'Klepi',
          firstname: 'Sonia',
          email: 'sonia.klepi@example.com',
        },
        booking_date: '2020-04-03T12:00:00Z',
        booking_token: 'ZEHBGD',
        booking_status: 'Validé',
      },
    ]
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
        },
        beneficiary: {
          lastname: 'Klepi',
          firstname: 'Sonia',
          email: 'sonia.klepi@example.com',
        },
        booking_date: '2020-04-03T12:00:00Z',
        booking_token: 'ZEHBGD',
        booking_status: 'Validé',
      },
    ])

    const booking = {
      stock: {
        offer_name: 'Avez-vous déjà vu',
      },
      beneficiary: {
        lastname: 'Klepi',
        firstname: 'Sonia',
        email: 'sonia.klepi@example.com',
      },
      booking_date: '2020-04-03T12:00:00Z',
      booking_token: 'ZEHBGD',
      booking_status: 'Validé',
    }
    const bookingsRecap = [booking]
    const newBooking = {
      stock: {
        offer_name: 'Merlin enchanteur',
      },
      beneficiary: {
        lastname: 'Klepi',
        firstname: 'Sonia',
        email: 'sonia.klepi@example.com',
      },
      booking_date: '2020-04-03T12:00:00Z',
      booking_token: 'ZEHBGD',
      booking_status: 'Validé',
    }
    const props = {
      bookingsRecap: bookingsRecap,
      isLoading: false,
    }
    const wrapper = shallow(<BookingsRecapTable {...props} />)

    // When
    wrapper.setState({ filters: { offerName: 'Avez', offerDate: null } })
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
      booking_status: 'Validé',
      booking_is_duo: false,
    }
    const props = {
      bookingsRecap: [booking],
      isLoading: false,
    }
    const wrapper = mount(<BookingsRecapTable {...props} />)
    const input = wrapper.find(Filters).find({ placeholder: 'Rechercher par nom d\'offre' })

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
            type: 'thing'
          },
          beneficiary: {
            lastname: 'Klepi',
            firstname: 'Sonia',
            email: 'sonia.klepi@example.com',
          },
          booking_date: '2020-04-03T12:00:00Z',
          booking_token: 'ZEHBGD',
          booking_status: 'Validé',
          booking_is_duo: false
        },
      ],
      isLoading: false,
    }
    filterBookingsRecap.mockReturnValue([])
    const wrapper = mount(<BookingsRecapTable {...props} />)

    const offerNameInput = wrapper.find(Filters).find({ placeholder: "Rechercher par nom d'offre" })
    await offerNameInput.simulate('change', { target: { value: 'not findable' } })

    const selectedDate = moment('2020-05-20')
    const offerDatePicker = wrapper.find(Filters).find(DatePicker)
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
    const offerDate = wrapper.find(Filters).find(DatePicker)
    expect(offerDate.prop('selected')).toBeNull()
  })
})
