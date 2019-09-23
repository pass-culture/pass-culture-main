import { shallow } from 'enzyme'
import React from 'react'

import Overlay from '../Overlay'

describe('src | components | layout | Overlay | Overlay', () => {
  let props

  beforeEach(() => {
    props = {
      isVisible: false,
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<Overlay {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
