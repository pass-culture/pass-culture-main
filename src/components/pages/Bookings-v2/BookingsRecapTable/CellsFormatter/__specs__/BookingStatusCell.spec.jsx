import { shallow } from 'enzyme/build'
import React from 'react'
import BookingStatusCell from '../BookingStatusCell'

describe('components | pages | bookings-v2 | CellsFormatter | BookingsStatusCell', () => {
  it('should render a div with the corresponding tag value and tag classnames for the given status', () => {
    // Given
    const props = {
      bookingStatus: 'validated',
    }

    // When
    const wrapper = shallow(<BookingStatusCell {...props} />)
    const status = wrapper.find({ children: 'validé' })

    // Then
    expect(status.hasClass('booking-status-label')).toBe(true)
    expect(status.hasClass('booking-status-validated')).toBe(true)
  })

  it('should render a div with the default tag classname for an unknown status', () => {
    // Given
    const props = {
      bookingStatus: 'Unknown',
    }

    // When
    const wrapper = shallow(<BookingStatusCell {...props} />)
    const status = wrapper.find({ children: 'unknown' })

    // Then
    expect(status.hasClass('booking-status-label')).toBe(true)
    expect(status.hasClass('booking-status-default')).toBe(true)
  })
})
