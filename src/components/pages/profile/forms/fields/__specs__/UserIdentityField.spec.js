import React from 'react'
import { shallow } from 'enzyme'
import { UserIdentityField } from '../UserIdentityField'

describe('src | components | pages | profile | UserIdentityField', () => {
  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<UserIdentityField />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })
})
