import { shallow } from 'enzyme'
import React from 'react'
import Home from '../Home'

describe('src | components | pages | Home', () => {
  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<Home />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
