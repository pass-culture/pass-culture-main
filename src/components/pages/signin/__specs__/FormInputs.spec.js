import React from 'react'
import { shallow } from 'enzyme'

import FormInputs from '../FormInputs'

describe('src | components | pages | signin | FormInputs', () => {
  it('should match the snapshot', () => {
    // given
    const props = {}

    // when
    const wrapper = shallow(<FormInputs {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
