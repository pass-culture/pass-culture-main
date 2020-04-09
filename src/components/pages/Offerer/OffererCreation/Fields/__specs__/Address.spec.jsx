import React from 'react'
import { shallow } from 'enzyme'
import Address from '../Address'

describe('src | components | pages | Offerer | OffererCreation | Fields | Address', () => {
  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<Address />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
