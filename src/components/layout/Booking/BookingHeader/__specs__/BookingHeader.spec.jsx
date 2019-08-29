import React from 'react'
import { shallow } from 'enzyme'

import BookingHeader from '../BookingHeader'

describe('src | components | layout | Booking | BookingHeader ', () => {
  let props

  beforeEach(() => {
    props = {
      recommendation: {
        offer: {
          name: 'Titre de la recommendation',
          product: { name: 'Titre de la recommendation' },
          venue: { name: 'Titre de la venue ' },
        },
      },
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<BookingHeader {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
