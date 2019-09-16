import Icon from '../Icon'
import React from 'react'
import { shallow } from 'enzyme'

describe('src | components | layout | Icon', () => {
  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<Icon />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
