import { shallow } from 'enzyme'
import React from 'react'

import SigninContainer from '../SigninContainer'

describe('src | components | pages | signin | Index', () => {
  it('should match the snapshot', () => {
    // given
    const props = {}

    // when
    const wrapper = shallow(<SigninContainer {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
