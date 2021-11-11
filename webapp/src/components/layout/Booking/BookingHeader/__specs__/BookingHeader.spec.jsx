import { mount } from 'enzyme'
import React from 'react'

import BookingHeader from '../BookingHeader'

describe('src | components | BookingHeader', () => {
  it('should display a title and subtitle', () => {
    // Given
    const props = {
      offer: {
        name: 'Fake offer name',
        venue: {
          name: 'Fake venue name',
        },
      },
    }

    // when
    const wrapper = mount(<BookingHeader {...props} />)

    // then
    const title = wrapper.find({ children: 'Fake offer name' })
    const subtitle = wrapper.find({ children: 'Fake venue name' })
    expect(title).toHaveLength(1)
    expect(subtitle).toHaveLength(1)
  })
})
