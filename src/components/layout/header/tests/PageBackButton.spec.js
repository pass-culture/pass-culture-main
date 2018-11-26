// jest --env=jsdom ./src/components/layout/header/tests/PageBackButton --watch
import React from 'react'
import { shallow } from 'enzyme'

import { RawPageBackButton } from '../PageBackButton'

const routerProps = {
  history: { goBack: jest.fn() },
}

const componentDefaultProps = {
  className: '',
  disabled: false,
  theme: 'red',
}

describe('src | components | layout | header | PageBackButton', () => {
  it('should match snapshot with default props', () => {
    // given
    const props = { ...componentDefaultProps, ...routerProps }
    // when
    const wrapper = shallow(<RawPageBackButton {...props} />)
    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })
  it('should match snapshot with custom props', () => {
    // given
    const props = {
      ...routerProps,
      ...componentDefaultProps,
      className: 'testable-component',
      disabled: true,
      theme: 'purple',
    }
    // when
    const wrapper = shallow(<RawPageBackButton {...props} />)
    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })
})
