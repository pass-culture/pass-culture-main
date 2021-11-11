import { shallow } from 'enzyme'
import React from 'react'
import { Transition } from 'react-transition-group'

import Overlay from '../Overlay'

describe('src | components | Overlay', () => {
  it('should display a transition', () => {
    // Given
    const props = {
      isVisible: false,
    }

    // when
    const wrapper = shallow(<Overlay {...props} />)

    // then
    const transition = wrapper.find(Transition)
    expect(transition.prop('in')).toBe(false)
    expect(transition.prop('timeout')).toBe(500)
  })
})
