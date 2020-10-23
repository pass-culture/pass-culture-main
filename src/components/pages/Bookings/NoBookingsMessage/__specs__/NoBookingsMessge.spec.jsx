import { mount } from 'enzyme/build'
import React from 'react'

import NoBookingsMessage from '../NoBookingsMessage'

describe('components | pages | bookings-v2 | NoBookingsMessage', () => {
  it('should render no bookings message', () => {
    // When
    const wrapper = mount(<NoBookingsMessage />)

    // Then
    const noBookingsMessage = wrapper.find({ children: 'Aucune réservation pour le moment' })
    expect(noBookingsMessage).toHaveLength(1)
  })
})
