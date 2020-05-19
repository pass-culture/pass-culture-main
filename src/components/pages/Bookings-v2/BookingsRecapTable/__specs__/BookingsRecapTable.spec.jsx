import BookingsRecapTable, { NB_BOOKINGS_PER_PAGE } from '../BookingsRecapTable'
import Table from '../Table/Table'
import React from 'react'
import { mount, shallow } from 'enzyme'
import BookingIsDuoCell from '../CellsFormatter/BookingIsDuoCell'
import BeneficiaryCell from '../CellsFormatter/BeneficiaryCell'
import BookingDateCell from '../CellsFormatter/BookingDateCell'
import BookingTokenCell from '../CellsFormatter/BookingTokenCell'
import BookingStatusCell from '../CellsFormatter/BookingStatusCell'
import BookingOfferCell from '../CellsFormatter/BookingOfferCell'
import Header from '../Header/Header'

describe('components | BookingsRecapTable', () => {
  it('should call the Table component with columns and data props', () => {
    // Given
    const data = [
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
      bookingsRecap: data,
    }

    // When
    const wrapper = shallow(<BookingsRecapTable {...props} />)
    const table = wrapper.find('Table')

    // Then
    expect(table).toHaveLength(1)
    const tableProps = table.props()
    expect(tableProps['columns']).toHaveLength(6)
    expect(tableProps['data']).toHaveLength(2)
  })

  it('should render the expected table headers', () => {
    // Given
    const data = []

    const props = {
      bookingsRecap: data,
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
    expect(firstHeader.text()).toBe("Nom de l'offre")
    expect(secondHeader.text()).toBe('')
    expect(thirdHeader.text()).toBe('Bénéficiaire')
    expect(fourthHeader.text()).toBe('Réservation')
    expect(fifthHeader.text()).toBe('Contremarque')
    expect(sixthHeader.text()).toBe('Statut')
  })

  it('should render the expected table rows', () => {
    // Given
    const data = [
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
      bookingsRecap: data,
    }

    // When
    const wrapper = mount(<BookingsRecapTable {...props} />)

    // Then
    const bookingOfferCell = wrapper.find(BookingOfferCell)
    expect(bookingOfferCell).toHaveLength(1)
    expect(bookingOfferCell.props()).toStrictEqual({ offer: { offer_name: 'Avez-vous déjà vu' } })
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
    const data = [
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
      bookingsRecap: data,
      nbBookings: 1,
    }

    // When
    const wrapper = mount(<BookingsRecapTable {...props} />)

    // Then
    const table = wrapper.find(Table)
    expect(table).toHaveLength(1)
    expect(table.props()).toStrictEqual({
      columns: wrapper.state('columns'),
      data: data,
      nbBookingsPerPage: NB_BOOKINGS_PER_PAGE,
      total: 1,
    })
  })

  it('should render a Header component', () => {
    // given
    const data = [
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
      bookingsRecap: data,
      nbBookings: 1,
    }

    // When
    const wrapper = shallow(<BookingsRecapTable {...props} />)

    // Then
    const header = wrapper.find(Header)
    expect(header).toHaveLength(1)
    expect(header.props()).toStrictEqual({
      nbBookings: 1,
    })
  })
})
