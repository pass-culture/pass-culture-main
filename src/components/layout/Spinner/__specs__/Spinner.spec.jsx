import Spinner from '../Spinner'
import React from 'react'
import { shallow } from 'enzyme'

describe('src | components | layout | Spinner', () => {
  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<Spinner />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
