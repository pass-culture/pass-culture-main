import React from 'react'
import { shallow } from 'enzyme'

import HiddenField from '../HiddenField'

describe('src | components | forms | inputs | HiddenField', () => {
  let props

  beforeEach(() => {
    props = {
      name: 'input-name',
      validator: jest.fn(),
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<HiddenField {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  it('should render a Field with the right props', () => {
    // when
    const wrapper = shallow(<HiddenField {...props} />)

    // then
    expect(wrapper.prop('name')).toStrictEqual('input-name')
    expect(wrapper.prop('validate')).toStrictEqual(props.validator)
  })
})
