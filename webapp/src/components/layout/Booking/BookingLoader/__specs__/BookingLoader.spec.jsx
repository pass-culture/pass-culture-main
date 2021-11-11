import { mount } from 'enzyme'
import React from 'react'

import BookingLoader from '../BookingLoader'

describe('src | components | BookingLoader', () => {
  it('should display a sentence', () => {
    // when
    const wrapper = mount(<BookingLoader />)

    // then
    const sentence = wrapper.find({ children: 'Réservation en cours...' })
    expect(sentence).toHaveLength(1)
  })
})
