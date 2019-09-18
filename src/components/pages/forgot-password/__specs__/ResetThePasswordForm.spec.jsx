import React from 'react'
import { shallow } from 'enzyme'
import { ResetThePasswordForm } from '../ResetThePasswordForm'

describe('src | components | pages | forgot-password | ResetThePasswordForm', () => {
  it('should match the snapshot', () => {
    // given
    const props = { canSubmit: true, isLoading: false }

    // when
    const wrapper = shallow(<ResetThePasswordForm {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
