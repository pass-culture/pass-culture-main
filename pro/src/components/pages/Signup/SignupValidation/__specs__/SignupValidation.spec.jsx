import { mount, shallow } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Redirect, Router } from 'react-router-dom'

import * as pcapi from 'repository/pcapi/pcapi'
import { campaignTracker } from 'tracking/mediaCampaignsTracking'

import SignupValidation from '../SignupValidation'

jest.mock('repository/pcapi/pcapi', () => ({
  validateUser: jest.fn(),
}))

describe('src | components | pages | Signup | validation', () => {
  let history
  let props

  beforeEach(() => {
    history = createBrowserHistory()
    const notifyError = jest.fn()
    const notifySuccess = jest.fn()
    props = {
      match: {
        params: {
          token: 'AAA',
        },
      },
      notifyError,
      notifySuccess,
    }
  })

  afterEach(jest.resetAllMocks)

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
    expect(pcapi.validateUser).toHaveBeenCalledWith(props.match.params.token)
  })

  it('should call media campaign tracker on mount only', () => {
    // when on mount
    const wrapper = mount(
      <Router history={history}>
        <SignupValidation {...props} />
      </Router>
    )

    // then
    expect(campaignTracker.signUpValidation).toHaveBeenCalledTimes(1)

    // when rerender
    wrapper.setProps(props)

    // then
    expect(campaignTracker.signUpValidation).toHaveBeenCalledTimes(1)
  })

  describe('notifySuccess', () => {
    it('should display a notification with success message', () => {
      // given
      const wrapper = shallow(<SignupValidation {...props} />)

      // when
      wrapper.instance().notifySuccess()

      // then
      expect(props.notifySuccess).toHaveBeenCalledWith(
        'Votre compte a été créé. Vous pouvez vous connecter avec les identifiants que vous avez choisis.'
      )
    })
  })

  describe('notifyFailure', () => {
    it('should display a notification with error message', () => {
      // given
      const wrapper = shallow(<SignupValidation {...props} />)
      const payload = {
        errors: {
          global: ['error1', 'error2'],
        },
      }

      // when
      wrapper.instance().notifyFailure(payload)

      // then
      expect(props.notifyError).toHaveBeenCalledWith(['error1', 'error2'])
    })
  })
})
