import { shallow } from 'enzyme'
import React from 'react'

import Overlay from '../Overlay'

describe('src | components | layout | Overlay | Overlay', () => {
  let props = {}

  it('should match the snapshot', () => {
    // given
    const wrapper = shallow(<Overlay {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
