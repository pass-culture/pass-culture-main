import { shallow } from 'enzyme/build'
import React from 'react'
import BookingStatusCellHistory from '../BookingStatusCellHistory'

describe('cellsFormatter | BookingsStatusCellHistory', () => {
  it('should render a div with the corresponding tag value and tag classnames for the given status', () => {
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
    const wrapper = shallow(<BookingStatusCellHistory {...props} />)
    const status = wrapper.find('span')

    // Then
    expect(status.hasClass('bs-history-datetime-booked')).toBe(true)
    expect(status.text()).toBe('Réservé : 04/01/2020 20:31')
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
      ],
    }

    // When
    const wrapper = shallow(<BookingStatusCellHistory {...props} />)
    const bookingStatusesElements = wrapper.find('li')

    // Then
    expect(bookingStatusesElements).toHaveLength(3)
  })
})
