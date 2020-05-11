import React from 'react'
import { shallow } from 'enzyme'
import Titles from '../../../layout/Titles/Titles'
import BookingsRecap from '../BookingsRecap'
import BookingsRecapTable from '../BookingsRecapTable/BookingsRecapTable'

function flushPromises() {
  return new Promise(resolve => setImmediate(resolve))
}

describe('src | components | pages | Bookings-v2', () => {
  let mockJsonPromise
  let mockFetchPromise

  beforeEach(() => {
    mockJsonPromise = Promise.resolve([{}])
    mockFetchPromise = Promise.resolve({
      json: () => mockJsonPromise,
    })
    jest.spyOn(global, 'fetch').mockImplementation(() => mockFetchPromise)
  })

  it('should render a Titles component and a BookingsRecapTable', async () => {
    // When
    const wrapper = shallow(<BookingsRecap />)

    // Then
    const title = wrapper.find(Titles)
    expect(title).toHaveLength(1)
    const bookingsTable = wrapper.find(BookingsRecapTable)
    expect(bookingsTable).toHaveLength(1)
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
    mockJsonPromise = Promise.resolve([oneBooking])

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

  it('should render the BookingsRecapTable with duplicated booking data together when booking is duo', async () => {
    // Given
    const oneDuoBooking = {
      beneficiary: { email: 'user@example.com', firstname: 'First', lastname: 'Last' },
      booking_date: '2020-04-12T19:31:12Z',
      booking_is_duo: true,
      booking_status: 'reimbursed',
      booking_token: 'TOKEN',
      stock: { offer_name: 'My offer name' },
    }
    const oneNonDuoBooking = {
      beneficiary: { email: 'another@example.com', firstname: 'An', lastname: 'Other' },
      booking_date: '2020-02-22T19:31:12Z',
      booking_is_duo: false,
      booking_status: 'booked',
      booking_token: 'NEKOT',
      stock: { offer_name: 'My other offer name' },
    }
    mockJsonPromise = Promise.resolve([oneDuoBooking, oneNonDuoBooking])

    // When
    const wrapper = shallow(<BookingsRecap />)

    // Then
    await flushPromises()
    const title = wrapper.find(Titles)
    expect(title).toHaveLength(1)
    const bookingsTable = wrapper.find(BookingsRecapTable)
    expect(bookingsTable).toHaveLength(1)
    expect(bookingsTable.prop('bookingsRecap')).toStrictEqual([
      oneDuoBooking,
      oneDuoBooking,
      oneNonDuoBooking,
    ])
  })
})
