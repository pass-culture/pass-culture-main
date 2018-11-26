// jest --env=jsdom ./src/components/layout/header/tests/PageSubmitButton --watch
import React from 'react'
import { shallow } from 'enzyme'

import PageSubmitButton from '../PageSubmitButton'

const componentDefaultProps = {
  className: '',
  disabled: false,
  isloading: false,
  theme: 'red',
}

describe('src | components | layout | header | PageSubmitButton', () => {
  it('should match snapshot with default props', () => {
    // given
    const props = { ...componentDefaultProps }
    // when
    const wrapper = shallow(<PageSubmitButton {...props} />)
    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })
  it('should match snapshot with custom props', () => {
    // given
    const props = {
      ...componentDefaultProps,
      className: '',
      disabled: true,
      isloading: false,
      theme: 'green',
    }
    // when
    const wrapper = shallow(<PageSubmitButton {...props} />)
    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })
  it('should match snapshot with custom props', () => {
    // given
    const props = {
      ...componentDefaultProps,
      className: '',
      disabled: true,
      isloading: true,
      theme: 'purple',
    }
    // when
    const wrapper = shallow(<PageSubmitButton {...props} />)
    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })
})
