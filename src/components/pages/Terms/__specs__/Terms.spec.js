import React from 'react'
import { shallow } from 'enzyme'
import Terms from '../Terms'

describe('src | components | pages | Terms', () => {
  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<Terms />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
