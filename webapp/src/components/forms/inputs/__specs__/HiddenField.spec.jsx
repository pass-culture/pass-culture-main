import { shallow } from 'enzyme'
import React from 'react'

import HiddenField from '../HiddenField'

describe('src | components | forms | inputs | HiddenField', () => {
  let props

  beforeEach(() => {
    props = {
      name: 'input-name',
      validator: jest.fn(),
    }
  })

  it('should render a Field with the right props', () => {
    // when
    const wrapper = shallow(<HiddenField {...props} />)

    // then
    expect(wrapper.prop('name')).toBe('input-name')
    expect(wrapper.prop('validate')).toBe(props.validator)
  })
})
