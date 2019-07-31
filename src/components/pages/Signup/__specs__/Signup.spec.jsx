import { shallow } from 'enzyme'
import React from 'react'

import Signup from '../Signup'

describe('src | components | pages | Signup', () => {
  it('should match the snapshot', () => {
    // given
    const props = {
      errors: {},
    }

    // when
    const wrapper = shallow(<Signup {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
