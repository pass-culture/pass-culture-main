import React from 'react'
import { shallow } from 'enzyme'

import Insert from '../Insert'

describe('src | components | layout | Insert', () => {
  it('should match the snapshot', () => {
    // given
    const props = null

    // when
    const wrapper = shallow(<Insert {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
