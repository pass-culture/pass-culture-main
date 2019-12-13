import { mount } from 'enzyme'
import React from 'react'
import { Router } from 'react-router-dom'

import SignIn from '../SignIn'
import EmailField from '../../../forms/inputs/EmailField'
import PasswordField from '../../../forms/inputs/PasswordField'

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
      history,
      query: {},
      signIn: jest.fn()
    }
  })

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
      wrapper.find(EmailField).find('input').simulate('change', { target: { value: 'pc-beneficiary@example.com' } })
      wrapper.find(PasswordField).find('input').simulate('change', { target: { value: 'abcdef1234' } })
      const signInButton = wrapper.findWhere(node => node.text() === 'Connexion').first()

      // when
      signInButton.simulate('submit')

      // then
      expect(props.signIn).toHaveBeenCalledWith(
        { 'identifier': 'pc-beneficiary@example.com', 'password': 'abcdef1234' },
        expect.any(Function),
        expect.any(Function)
      )
    })

    it('should redirect to discovery page when user sign in succeeded', async () => {
      // given
      const mock = jest.fn()
      props.signIn = jest.spyOn(props, 'signIn').mockImplementation((values, fail, success) => {
        new Promise(resolve => resolve())
          .then(success(mock)())
      })
      const wrapper = mount(
        <Router history={history}>
          <SignIn {...props} />
        </Router>
      )
      wrapper.find(EmailField).find('input').simulate('change', { target: { value: 'pc-beneficiary@example.com' } })
      wrapper.find(PasswordField).find('input').simulate('change', { target: { value: 'abcdef1234' } })
      const signInButton = wrapper.findWhere(node => node.text() === 'Connexion').first()

      // when
      await signInButton.simulate('submit')

      // then
      expect(history.push).toHaveBeenCalledWith('/decouverte')
    })

    it('should display inputs error when user sign in failed', async () => {
      // given
      const state = {}
      const mock = jest.fn()
      const action = {
        payload: {
          errors: ['error1']
        }
      }
      props.signIn = jest.spyOn(props, 'signIn').mockImplementation((values, fail) => {
        new Promise(resolve => resolve())
          .catch(fail(mock)(state, action))
      })
      const wrapper = mount(
        <Router history={history}>
          <SignIn {...props} />
        </Router>
      )
      wrapper.find(EmailField).find('input').simulate('change', { target: { value: 'pc-beneficiary@example.com' } })
      wrapper.find(PasswordField).find('input').simulate('change', { target: { value: 'abcdef1234' } })
      const signInButton = wrapper.findWhere(node => node.text() === 'Connexion').first()

      // when
      await signInButton.simulate('submit')

      // then
      expect(mock).toHaveBeenCalledWith({ 0: 'error1' })
    })
  })
})
