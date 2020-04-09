import React from 'react'
import { shallow } from 'enzyme'
import City from '../City'

describe('src | components | pages | Offerer | OffererCreation | Fields | City', () => {
  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<City />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
