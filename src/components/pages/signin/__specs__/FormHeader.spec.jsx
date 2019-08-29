import React from 'react'
import { shallow } from 'enzyme'

import FormHeader from '../FormHeader'

describe('src | components | pages | signin | FormHeader', () => {
  it('should match the snapshot', () => {
    // given
    const props = {}

    // when
    const wrapper = shallow(<FormHeader {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
