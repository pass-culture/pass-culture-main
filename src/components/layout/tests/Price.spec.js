// jest ./src/components/layout/tests/Price --watch
import React from 'react'
import { shallow } from 'enzyme'

import Price from '../Price'

describe('src | components | pages | Price', () => {
  it('should match snapshot without props', () => {
    // given
    const props = {}
    // when
    const wrapper = shallow(<Price {...props} />)
    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })
  it('should match snapshot with a price number', () => {
    // given
    const props = { value: 5 }
    // when
    const wrapper = shallow(<Price {...props} />)
    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })
  it('should match snapshot with an array of prices number', () => {
    // given
    const props = { value: [5, 10] }
    // when
    const wrapper = shallow(<Price {...props} />)
    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })
  it('should match snapshot with a classname', () => {
    // given
    const props = { className: 'fake-css-class', value: [5, 10] }
    // when
    const wrapper = shallow(<Price {...props} />)
    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })
  it('should match snapshot free prop defined and a zero price', () => {
    // given
    const props = { free: 'Offre gratuite', value: 0 }
    // when
    const wrapper = shallow(<Price {...props} />)
    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })
})
