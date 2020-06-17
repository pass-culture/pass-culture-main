import { shallow } from 'enzyme/build'
import React from 'react'
import BookingStatusCell from '../BookingStatusCell'

describe('CellsFormatter | BookingsStatusCellHistory', () => {
  it('should render a div with the corresponding tag value and tag classnames for the given status', () => {
    // Given
    const props = {
      bookingRecapInfo: {
        original: {
          stock: {
            event_beginning_datetime: '2020-06-05T16:31:59.102163+02:00',
            offer_name: 'Matrix',
            type: 'event',
          },
          booking_is_duo: true,
          beneficiary: {
            email: 'loulou.duck@example.com',
            firstname: 'Loulou',
            lastname: 'Duck',
          },
          booking_date: '2020-01-04T20:31:12+01:00',
          booking_token: '5U7M6U',
          booking_status: 'validated',
          booking_recap_history: {
            booking_date: '2020-01-04T20:31:12+01:00',
          }
        },
      },
    }

    // When
    const wrapper = shallow(<BookingStatusCell {...props} />)
    const status = wrapper.find({ children: 'validé' })

    // Then
    expect(status.hasClass('booking-status-label')).toBe(true)
    expect(status.hasClass('booking-status-validated')).toBe(true)
  })
})
