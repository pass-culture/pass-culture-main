import { shallow } from 'enzyme'
import React from 'react'
import Draggable from 'react-draggable'

import Navigation from '../Navigation'

describe('src | components | Navigation', () => {
  it('should display the draggable', () => {
    // given
    const props = {
      distanceClue: '',
      flipHandler: jest.fn(),
      height: 500,
      priceRange: [],
      separator: '-',
      trackConsultOffer: jest.fn(),
    }

    // when
    const wrapper = shallow(<Navigation {...props} />)

    // then
    const draggable = wrapper.find(Draggable)
    expect(draggable.prop('axis')).toBe('y')
    expect(draggable.prop('bounds')).toStrictEqual({ bottom: 0, left: 0, right: 0, top: 0 })
    expect(draggable.prop('onStop')).toStrictEqual(expect.any(Function))
  })
})
