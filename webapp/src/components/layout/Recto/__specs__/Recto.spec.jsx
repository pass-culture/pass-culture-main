import { shallow } from 'enzyme'
import React from 'react'

import Recto from '../Recto'
import Thumb from '../Thumb'

describe('src | components | Recto', () => {
  it('should display a thumb', () => {
    // given
    const props = {
      areDetailsVisible: true,
      thumbUrl: '/fake-url',
    }

    // when
    const wrapper = shallow(<Recto {...props} />)

    // then
    const thumb = wrapper.find(Thumb)
    expect(thumb.prop('src')).toBe('/fake-url')
    expect(thumb.prop('translated')).toBe(true)
  })
})
