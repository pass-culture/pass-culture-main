import { mount, shallow } from 'enzyme'
import React from 'react'
import { Router } from 'react-router-dom'

import Signin from '../Signin'

describe('src | components | pages | signin | Signin', () => {
  let props

  beforeEach(() => {
    props = {
      submitSigninForm: jest.fn(),
      history: {},
      query: {},
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<Signin {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  it('should have sign in button and sign up link', () => {
    // given
    const history = {
      createHref: jest.fn(),
      goBack: jest.fn(),
      listen: jest.fn(),
      location: {
        pathname: 'fake-url/',
      },
      push: jest.fn(),
      replace: jest.fn(),
    }

    // when
    const wrapper = mount(
      <Router history={history}>
        <Signin {...props} />
      </Router>
    )

    // then
    const signUpLink = wrapper.find('#sign-up-link')
    const signInButton = wrapper.find('#signin-submit-button')
    const targetUrl = signUpLink.at(0).props().href
    expect(signInButton).toHaveLength(1)
    expect(signUpLink).toHaveLength(1)
    expect(targetUrl).toBe(
      'https://www.demarches-simplifiees.fr/commencer/inscription-pass-culture'
    )
  })

  describe('handleOnFormSubmit', () => {
    it('should set isLoading state to true', () => {
      // given
      const formValues = {
        identifier: 'name@email.com',
        password: 'SomePassWord',
      }
      const wrapper = shallow(<Signin {...props} />)

      // when
      wrapper.instance().handleOnFormSubmit(formValues)

      // then
      expect(wrapper.state()).toStrictEqual({
        isLoading: true,
      })
    })

    it('should call submitSigninForm from container', () => {
      // given
      const formValues = {
        identifier: 'name@email.com',
        password: 'SomePassWord',
      }
      const wrapper = shallow(<Signin {...props} />)

      // when
      wrapper.instance().handleOnFormSubmit(formValues)

      // then
      expect(props.submitSigninForm).toHaveBeenCalledWith(
        formValues,
        wrapper.instance().handleRequestFail,
        wrapper.instance().handleRequestSuccess
      )
    })
  })
})
