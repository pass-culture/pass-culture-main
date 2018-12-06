// jest --env=jsdom ./src/components/layout/header/tests/PageCloseButton --watch
import React from 'react'
import { shallow } from 'enzyme'

import { RawPageCloseButton } from '../PageCloseButton'

const routerProps = {
  history: { push: jest.fn() },
}

const componentDefaultProps = {
  baseurl: 'decouverte',
  className: '',
  disabled: false,
  theme: 'red',
}

describe('src | components | layout | header | PageCloseButton', () => {
  it('should match snapshot with default props', () => {
    // given
    const props = { ...routerProps, ...componentDefaultProps }

    // when
    const wrapper = shallow(<RawPageCloseButton {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })
  it('should match snapshot with custom props', () => {
    // given
    const props = {
      ...routerProps,
      ...componentDefaultProps,
      baseurl: 'profil',
      className: 'testable-component',
      disabled: true,
      theme: 'purple',
    }

    // when
    const wrapper = shallow(<RawPageCloseButton {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })
})
