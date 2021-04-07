import { mount } from 'enzyme'
import React from 'react'
import { Router } from 'react-router-dom'

import SignIn from '../SignIn'
import EmailField from '../../../forms/inputs/EmailField'
import PasswordField from '../../../forms/inputs/PasswordField'
import { campaignTracker } from '../../../../tracking/mediaCampaignsTracking'

describe('component | SignIn', () => {
  let props
  let history

  beforeEach(() => {
    history = {
      createHref: jest.fn(),
      goBack: jest.fn(),
      listen: jest.fn(),
      location: {
        pathname: '',
      },
      push: jest.fn(),
      replace: jest.fn(),
    }
    props = {
      homepageIsDisabled: true,
      history,
      query: {},
      signIn: jest.fn(),
    }
    props.signIn = jest.spyOn(props, 'signIn').mockImplementation((values, fail, success) => {
      new Promise(resolve => resolve()).then(success(jest.fn())())
    })
  })

  afterEach(jest.clearAllMocks)

  describe('when render', () => {
    it('should have sign in and cancel buttons', () => {
      // when
      const wrapper = mount(
        <Router history={history}>
          <SignIn {...props} />
        </Router>
      )

      // then
      const cancelButton = wrapper.findWhere(node => node.text() === 'Annuler').first()
      const signInButton = wrapper.findWhere(node => node.text() === 'Connexion').first()
      expect(signInButton).toHaveLength(1)
      expect(cancelButton).toHaveLength(1)
    })

    it('should trigger sign in when user has filled email, password and clicked on sign in button', () => {
      // given
      const wrapper = mount(
        <Router history={history}>
          <SignIn {...props} />
        </Router>
      )
      wrapper
        .find(EmailField)
        .find('input')
        .simulate('change', { target: { value: 'pc-beneficiary@example.com' } })
      wrapper
        .find(PasswordField)
        .find('input')
        .simulate('change', { target: { value: 'a!@d1d@#bcdeFf1234' } })
      const signInButton = wrapper.findWhere(node => node.text() === 'Connexion').first()

      // when
      signInButton.simulate('submit')

      // then
      expect(props.signIn).toHaveBeenCalledWith(
        { identifier: 'pc-beneficiary@example.com', password: 'a!@d1d@#bcdeFf1234' },
        expect.any(Function),
        expect.any(Function)
      )
    })

    it('should fail to trigger sign in when form is incorrect and user click on sign in button', () => {
      // given
      const wrapper = mount(
        <Router history={history}>
          <SignIn {...props} />
        </Router>
      )
      wrapper
        .find(EmailField)
        .find('input')
        .simulate('change', { target: { value: '' } })
      wrapper
        .find(PasswordField)
        .find('input')
        .simulate('change', { target: { value: 'abcdef1234' } })
      const signInButton = wrapper.findWhere(node => node.text() === 'Connexion').first()

      // when
      signInButton.simulate('submit')

      // then
      expect(props.signIn).not.toHaveBeenCalledWith(
        { identifier: '', password: 'abcdef1234' },
        expect.any(Function),
        expect.any(Function)
      )
    })

    it('should redirect to discovery page when user sign in succeeded and homepage feature is disabled', () => {
      // given
      const wrapper = mount(
        <Router history={history}>
          <SignIn {...props} />
        </Router>
      )
      wrapper
        .find(EmailField)
        .find('input')
        .simulate('change', { target: { value: 'pc-beneficiary@example.com' } })
      wrapper
        .find(PasswordField)
        .find('input')
        .simulate('change', { target: { value: 'abcdef@!E4C12q1234' } })
      const signInButton = wrapper.findWhere(node => node.text() === 'Connexion').first()

      // when
      signInButton.simulate('submit')

      // then
      expect(history.push).toHaveBeenCalledWith('/decouverte')
    })

    it('should redirect to home page when user sign in succeeded and homepage feature is enabled', () => {
      // given
      props.homepageIsDisabled = false
      const wrapper = mount(
        <Router history={history}>
          <SignIn {...props} />
        </Router>
      )
      wrapper
        .find(EmailField)
        .find('input')
        .simulate('change', { target: { value: 'pc-beneficiary@example.com' } })
      wrapper
        .find(PasswordField)
        .find('input')
        .simulate('change', { target: { value: 'abcdeFEW56124e!ff1234' } })
      const signInButton = wrapper.findWhere(node => node.text() === 'Connexion').first()

      // when
      signInButton.simulate('submit')

      // then
      expect(history.push).toHaveBeenCalledWith('/accueil')
    })

    it('should display inputs error when user sign in failed', () => {
      // given
      const state = {}
      const mock = jest.fn()
      const action = {
        payload: {
          errors: ['error1'],
        },
      }
      props.signIn = jest.spyOn(props, 'signIn').mockImplementation((values, fail) => {
        new Promise(resolve => resolve()).catch(fail(mock)(state, action))
      })
      const wrapper = mount(
        <Router history={history}>
          <SignIn {...props} />
        </Router>
      )
      wrapper
        .find(EmailField)
        .find('input')
        .simulate('change', { target: { value: 'pc-beneficiary@example.com' } })
      wrapper
        .find(PasswordField)
        .find('input')
        .simulate('change', { target: { value: 'abcde!4f32563Ff1234' } })
      const signInButton = wrapper.findWhere(node => node.text() === 'Connexion').first()

      // when
      signInButton.simulate('submit')

      // then
      expect(mock).toHaveBeenCalledWith({ 0: 'error1' })
    })

    it('should call media campaign tracker on mount only', () => {
      // when mount
      const wrapper = mount(
        <Router history={history}>
          <SignIn {...props} />
        </Router>
      )

      // Then
      expect(campaignTracker.signin).toHaveBeenCalledTimes(1)

      // when rerender
      wrapper.setProps({})

      // Then
      expect(campaignTracker.signin).toHaveBeenCalledTimes(1)
    })
  })
})
