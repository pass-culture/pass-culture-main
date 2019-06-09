import { shallow } from 'enzyme'
import React from 'react'

import { Footer } from '../Footer'

describe('src | components | pages | search | Footer', () => {
  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<Footer />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })
})
