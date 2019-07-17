import React from 'react'
import SignupForm from '../SignupForm'
import { shallow } from 'enzyme'
import { SubmitButton } from 'pass-culture-shared'

describe('src | components | pages | Signup | SignupForm', () => {
  let props

  beforeEach(() => {
    props = {
      errors: [],
      offererName: 'super structure',
      patch: {}
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<SignupForm {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    it('should render a disabled submit button when required inputs are not filled', () => {
      // when
      const wrapper = shallow(<SignupForm {...props} />)

      // then
      const submitButton = wrapper
        .find(SubmitButton).dive()
        .find('button')
      expect(submitButton.prop('disabled')).toBe(true)
    })
  })
})
