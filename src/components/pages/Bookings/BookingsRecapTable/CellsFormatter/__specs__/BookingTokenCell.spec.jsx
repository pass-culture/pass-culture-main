import { shallow } from 'enzyme/build'
import React from 'react'
import BookingTokenCell from '../BookingTokenCell'

describe('components | pages | bookings-v2 | CellsFormatter | BookingsTokenCell', () => {
  it('should render a booking token when value is provided', () => {
    // Given
    const props = {
      bookingToken: 'ABCDEF',
    }

    // When
    const wrapper = shallow(<BookingTokenCell {...props} />)

    // Then
    const token = wrapper.find({ children: props.bookingToken })
    expect(token).toHaveLength(1)
  })

  it('should render a hyphen when value is not provided', () => {
    // Given
    const props = {
      bookingToken: null,
    }

    // When
    const wrapper = shallow(<BookingTokenCell {...props} />)

    // Then
    const token = wrapper.find({ children: '-' })
    expect(token).toHaveLength(1)
  })
})
