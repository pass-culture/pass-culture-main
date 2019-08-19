import React from 'react'
import { shallow } from 'enzyme'

import BookingSuccess from '../BookingSuccess'

describe('src | components | pages | search | BookingSuccess', () => {
  it('should match the snapshot', () => {
    // given
    const props = {
      data: {
        token: 'G8G8G8',
      },
      isEvent: true,
    }

    // when
    const wrapper = shallow(<BookingSuccess {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
