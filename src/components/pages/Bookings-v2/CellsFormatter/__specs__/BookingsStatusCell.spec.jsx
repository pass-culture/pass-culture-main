import { shallow } from 'enzyme/build'
import React from 'react'
import BookingStatusCell from '../BookingsStatusCell'

describe('components | pages | bookings-v2 | CellsFormatter | BookingsStatusCell', () => {
  it('should render a div with XXXXXXXXXXXXXX', () => {
    // Given
    const props = {
      bookingStatusInfos: 'Validé',
    }

    // When
    const wrapper = shallow(<BookingStatusCell {...props} />)

    // Then
    expect(wrapper).toBeNull()
  })
})
