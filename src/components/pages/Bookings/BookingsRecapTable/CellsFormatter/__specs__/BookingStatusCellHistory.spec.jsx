import { mount } from 'enzyme/build'
import React from 'react'

import BookingStatusCellHistory from '../BookingStatusCellHistory'

describe('cellsFormatter | BookingsStatusCellHistory', () => {
  it('should render a div with the corresponding status and date for the given status', () => {
    // Given
    const props = {
      bookingStatusHistory: [
        {
          status: 'booked',
          date: '2020-01-04T20:31:12+01:00',
        },
      ],
    }

    // When
    const wrapper = mount(<BookingStatusCellHistory {...props} />)

    // Then
    const status = wrapper.find('li')
    const disc = status.find('span')
    expect(disc.hasClass('bs-history-booked')).toBe(true)
    expect(status.text()).toBe('réservé : 04/01/2020 20:31')
  })

  it('should render a list with as many elements as statuses', () => {
    // Given
    const props = {
      bookingStatusHistory: [
        {
          status: 'booked',
          date: '2020-01-04T20:31:12+01:00',
        },
        {
          status: 'validated',
          date: '2020-01-05T20:31:12+01:00',
        },
        {
          status: 'reimbursed',
          date: '2020-01-06T20:31:12+01:00',
        },
        {
          status: 'confirmed',
          date: '2020-01-06T20:31:12+01:00',
        },
      ],
    }

    // When
    const wrapper = mount(<BookingStatusCellHistory {...props} />)

    // Then
    const bookingStatusesElements = wrapper.find('li')
    expect(bookingStatusesElements).toHaveLength(4)
  })

  it('should render only date and not time for reimbursed status history', () => {
    // Given
    const props = {
      bookingStatusHistory: [
        {
          status: 'reimbursed',
          date: '2020-01-06T20:31:12+01:00',
        },
      ],
    }

    // When
    const wrapper = mount(<BookingStatusCellHistory {...props} />)

    // Then
    const status = wrapper.find('li')
    const disc = status.find('span')
    expect(disc.hasClass('bs-history-reimbursed')).toStrictEqual(true)
    expect(status.text()).toBe('remboursé : 06/01/2020')
  })

  it('should render a "-" when the date is not available', () => {
    // Given
    const props = {
      bookingStatusHistory: [
        {
          status: 'reimbursed',
          date: null,
        },
      ],
    }

    // When
    const wrapper = mount(<BookingStatusCellHistory {...props} />)

    // Then
    const status = wrapper.find('li')
    const disc = status.find('span')
    expect(disc.hasClass('bs-history-reimbursed')).toStrictEqual(true)
    expect(status.text()).toBe('remboursé : -')
  })
})
