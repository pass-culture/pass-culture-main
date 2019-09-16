import Ribbon from '../Ribbon'
import React from 'react'
import { shallow } from 'enzyme'

describe('src | components | layout | Ribbon', () => {
  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<Ribbon />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
