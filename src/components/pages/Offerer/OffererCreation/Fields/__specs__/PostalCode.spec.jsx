import React from 'react'
import { shallow } from 'enzyme'
import PostalCode from '../PostalCode'

describe('src | components | pages | Offerer | OffererCreation | Fields | PostalCode', () => {
  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<PostalCode />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
