import React from 'react'
import { shallow } from 'enzyme'
import Titles from 'components/layout/Titles/Titles'
import BookingsRecap from '../BookingsRecap'
import BookingsRecapTable from '../BookingsRecapTable/BookingsRecapTable'
import * as bookingRecapsService from '../../../../services/bookingsRecapService'
import NoBookingsMessage from '../NoBookingsMessage/NoBookingsMessage'
import Spinner from 'components/layout/Spinner'

function flushPromises() {
  return new Promise(resolve => setImmediate(resolve))
}

describe('components | BookingsRecap', () => {
  let fetchBookingsRecapByPageStub

  let fetchBookingsRecapByPageSpy
  beforeEach(() => {
    fetchBookingsRecapByPageStub = Promise.resolve({
      bookings_recap: [],
      page: 0,
      pages: 0,
      total: 0,
    })
    fetchBookingsRecapByPageSpy = jest
      .spyOn(bookingRecapsService, 'fetchBookingsRecapByPage')
      .mockImplementation(() => fetchBookingsRecapByPageStub)
  })

  afterEach(() => {
    fetchBookingsRecapByPageSpy.mockReset()
  })

  it('should render a Titles component and a NoBookingsMessage when api returned no bookings', async () => {
    // When
    const wrapper = shallow(<BookingsRecap />)

    // Then
    await flushPromises()
    const title = wrapper.find(Titles)
    expect(title).toHaveLength(1)
    const bookingsTable = wrapper.find(BookingsRecapTable)
    expect(bookingsTable).toHaveLength(0)
    const noBookingsMessage = wrapper.find(NoBookingsMessage)
    expect(noBookingsMessage).toHaveLength(1)
    const spinner = wrapper.find(Spinner)
    expect(spinner).toHaveLength(0)
  })

  it('should render a Titles component and a BookingsRecapTable when api returned at least one booking', async () => {
    // Given
    const oneBooking = {
      beneficiary: { email: 'user@example.com', firstname: 'First', lastname: 'Last' },
      booking_date: '2020-04-12T19:31:12Z',
      booking_is_duo: false,
      booking_status: 'reimbursed',
      booking_token: 'TOKEN',
      stock: { offer_name: 'My offer name' },
    }
    const paginatedBookingRecapReturned = {
      page: 1,
      pages: 1,
      total: 1,
      bookings_recap: [oneBooking],
    }
    fetchBookingsRecapByPageStub = Promise.resolve(paginatedBookingRecapReturned)

    // When
    const wrapper = shallow(<BookingsRecap />)

    // Then
    await flushPromises()
    const title = wrapper.find(Titles)
    expect(title).toHaveLength(1)
    const bookingsTable = wrapper.find(BookingsRecapTable)
    expect(bookingsTable).toHaveLength(1)
    const noBookingsMessage = wrapper.find(NoBookingsMessage)
    expect(noBookingsMessage).toHaveLength(0)
    const spinner = wrapper.find(Spinner)
    expect(spinner).toHaveLength(0)
  })

  it('should fetch bookings as many time as the number of pages', async () => {
    // Given
    const bookings1 = {
      beneficiary: { email: 'user@example.com', firstname: 'First', lastname: 'Last' },
      booking_date: '2020-04-12T19:31:12Z',
      booking_is_duo: false,
      booking_status: 'reimbursed',
      booking_token: 'TOKEN',
      stock: { offer_name: 'My offer name' },
    }
    const bookings2 = {
      beneficiary: { email: 'user@example.com', firstname: 'First', lastname: 'Last' },
      booking_date: '2020-04-12T19:31:12Z',
      booking_is_duo: false,
      booking_status: 'reimbursed',
      booking_token: 'TOKEN',
      stock: { offer_name: 'My offer name' },
    }
    const paginatedBookingRecapReturned = {
      page: 1,
      pages: 2,
      total: 2,
      bookings_recap: [bookings1],
    }
    const secondPaginatedBookingRecapReturned = {
      page: 2,
      pages: 2,
      total: 2,
      bookings_recap: [bookings2],
    }
    fetchBookingsRecapByPageSpy
      .mockResolvedValueOnce(paginatedBookingRecapReturned)
      .mockResolvedValueOnce(secondPaginatedBookingRecapReturned)

    // When
    const wrapper = shallow(<BookingsRecap />)

    // Then
    await flushPromises()
    expect(fetchBookingsRecapByPageSpy).toHaveBeenCalledTimes(2)
    expect(fetchBookingsRecapByPageSpy).toHaveBeenNthCalledWith(1)
    expect(fetchBookingsRecapByPageSpy).toHaveBeenNthCalledWith(2, 2)
    const bookingsTable = wrapper.find(BookingsRecapTable)
    expect(bookingsTable.props()).toStrictEqual({
      bookingsRecap: [bookings1, bookings2],
      isLoading: false,
    })
  })

  it('should render the BookingsRecapTable with api values', async () => {
    // Given
    const oneBooking = {
      beneficiary: { email: 'user@example.com', firstname: 'First', lastname: 'Last' },
      booking_date: '2020-04-12T19:31:12Z',
      booking_is_duo: false,
      booking_status: 'reimbursed',
      booking_token: 'TOKEN',
      stock: { offer_name: 'My offer name' },
    }
    const paginatedBookingRecapReturned = {
      page: 1,
      pages: 1,
      total: 1,
      bookings_recap: [oneBooking],
    }
    fetchBookingsRecapByPageStub = Promise.resolve(paginatedBookingRecapReturned)

    // When
    const wrapper = shallow(<BookingsRecap />)

    // Then
    await flushPromises()
    const title = wrapper.find(Titles)
    expect(title).toHaveLength(1)
    const bookingsTable = wrapper.find(BookingsRecapTable)
    expect(bookingsTable).toHaveLength(1)
    expect(bookingsTable.prop('bookingsRecap')).toStrictEqual([oneBooking])
  })

  it('should render a spinner when data from first page are still loading', async () => {
    // When
    const wrapper = shallow(<BookingsRecap />)

    // Then
    const spinner = wrapper.find(Spinner)
    expect(spinner).toHaveLength(1)
  })

})
