import React from 'react'
import { shallow } from 'enzyme'

import Price from '../Price'

describe('src | components | pages | Price', () => {
  it('should match the snapshot without props', () => {
    // given
    const props = {}

    // when
    const wrapper = shallow(<Price {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  it('should match the snapshot with a price number', () => {
    // given
    const props = { value: 5 }

    // when
    const wrapper = shallow(<Price {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  it('should match the snapshot with an array of prices number', () => {
    // given
    const props = { value: [5, 10] }

    // when
    const wrapper = shallow(<Price {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  it('should match the snapshot with decimal prices', () => {
    // given
    const props = { value: [5.99, 10] }

    // when
    const wrapper = shallow(<Price {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  it('should match the snapshot free prop defined and a zero price', () => {
    // given
    const props = { value: 0 }

    // when
    const wrapper = shallow(<Price {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
