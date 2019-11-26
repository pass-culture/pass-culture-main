import React from 'react'
import { shallow } from 'enzyme'
import { RequestEmailForm } from '../RequestEmailForm'

describe('src | components | pages | forgot-password | RequestEmailForm', () => {
  it('should match the snapshot', () => {
    // given
    const props = { canSubmit: true, isLoading: false }

    // when
    const wrapper = shallow(<RequestEmailForm {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
