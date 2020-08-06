import { mount, shallow } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Redirect, Router } from 'react-router-dom'

import SignupValidation from '../SignupValidation'

describe('src | components | pages | Signup | validation', () => {
  let history
  let dispatch
  let props

  beforeEach(() => {
    history = createBrowserHistory()
    dispatch = jest.fn()
    props = {
      dispatch,
      match: {
        params: {
          token: 'AAA',
        },
      },
    }
  })

  it('should render a Redirect component', () => {
    // when
    const wrapper = mount(
      <Router history={history}>
        <SignupValidation {...props} />
      </Router>
    )

    // then
    const redirect = wrapper.find(Redirect)
    expect(redirect).toHaveLength(1)
    expect(redirect.prop('to')).toBe('/connexion')
  })

  it('should dispatch an action to verify validity of user token', () => {
    // when
    mount(
      <Router history={history}>
        <SignupValidation {...props} />
      </Router>
    )

    // then
    expect(dispatch.mock.calls[0][0]).toStrictEqual({
      config: {
        apiPath: '/validate/user/AAA',
        handleFail: expect.any(Function),
        handleSuccess: expect.any(Function),
        method: 'PATCH',
      },
      type: 'REQUEST_DATA_PATCH_/VALIDATE/USER/AAA',
    })
  })

  describe('notifySuccess', () => {
    it('should display a notification with success message', () => {
      // given
      const wrapper = shallow(<SignupValidation {...props} />)
      const notifySuccess = wrapper.instance().notifySuccess()

      // when
      notifySuccess()

      // then
      const notifySuccessCall = dispatch.mock.calls[1][0]
      expect(notifySuccessCall).toStrictEqual({
        patch: {
          text:
            'Votre compte a été créé. Vous pouvez vous connecter avec les identifiants que vous avez choisis.',
          type: 'success',
        },
        type: 'SHOW_NOTIFICATION',
      })
    })
  })

  describe('notifyFailure', () => {
    it('should display a notification with error message', () => {
      // given
      const wrapper = shallow(<SignupValidation {...props} />)
      const notifyFailure = wrapper.instance().notifyFailure()
      const state = {}
      const action = {
        payload: {
          errors: {
            global: ['error1', 'error2'],
          },
        },
      }

      // when
      notifyFailure(state, action)

      // then
      const notifyFailureCall = dispatch.mock.calls[1][0]
      expect(notifyFailureCall).toStrictEqual({
        patch: {
          text: ['error1', 'error2'],
          type: 'danger',
        },
        type: 'SHOW_NOTIFICATION',
      })
    })
  })
})
