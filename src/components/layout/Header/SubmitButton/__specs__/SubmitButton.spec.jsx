import React from 'react'
import { shallow } from 'enzyme/build'
import SubmitButton from '../SubmitButton'

describe('src | components | layout | Header | SubmitButton', () => {
  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<SubmitButton />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
