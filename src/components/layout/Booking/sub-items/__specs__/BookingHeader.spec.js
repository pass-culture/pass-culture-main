import React from 'react'
import { shallow } from 'enzyme'

import BookingHeader from '../BookingHeader'

describe('src | components | booking | BookingHeader', () => {
  it('should match the snapshot', () => {
    // given
    const props = {
      recommendation: {
        offer: {
          name: 'Titre de la recommendation',
          product: { name: 'Titre de la recommendation' },
          venue: { name: 'Titre de la venue ' },
        },
      },
    }

    // when
    const wrapper = shallow(<BookingHeader {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
