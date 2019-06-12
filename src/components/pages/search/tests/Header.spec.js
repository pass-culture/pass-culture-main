import { shallow } from 'enzyme'
import React from 'react'

import Header from '../Header'

describe('src | components | pages | search | Header', () => {
  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<Header title="Fake title" />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })
})
