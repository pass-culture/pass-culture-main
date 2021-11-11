import { shallow } from 'enzyme'
import React from 'react'
import { Transition } from 'react-transition-group'

import SharePopin from '../SharePopin'

describe('src | components | SharePopin', () => {
  it('should display a transition', () => {
    // given
    const props = {
      dispatch: jest.fn(),
      visible: true,
    }

    // when
    const wrapper = shallow(<SharePopin {...props} />)

    // then
    const transition = wrapper.find(Transition)
    expect(transition).toHaveLength(1)
  })
})
