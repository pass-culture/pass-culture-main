import React from 'react'
import { shallow } from 'enzyme'
import Name from '../Name'

describe('src | components | pages | Offerer | OffererCreation | Fields | Name', () => {
  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<Name />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
