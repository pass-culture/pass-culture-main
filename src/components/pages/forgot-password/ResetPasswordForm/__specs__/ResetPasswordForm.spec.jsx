import React from 'react'
import { shallow } from 'enzyme'
import { ResetPasswordForm } from '../ResetPasswordForm'

describe('src | components | pages | forgot-password | ResetPasswordForm', () => {
  it('should match the snapshot', () => {
    // given
    const props = { canSubmit: true, isLoading: false }

    // when
    const wrapper = shallow(<ResetPasswordForm {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
