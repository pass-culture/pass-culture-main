import React from 'react'
import { shallow } from 'enzyme'

import RelativeFooter from '../RelativeFooter'

describe('src | components | pages | RelativeFooter', () => {
  it('should match the snapshot', () => {
    // given
    const props = {
      theme: 'fakeTheme',
    }

    // when
    const wrapper = shallow(<RelativeFooter {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
