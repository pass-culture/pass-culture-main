import { mount, shallow } from 'enzyme'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import configureStore from 'store'

import LostPassword from '../LostPassword'

describe('src | components | pages | LostPassword', () => {
  let props

  beforeEach(() => {
    props = {
      change: false,
      envoye: false,
      isNewHomepageActive: true,
      token: 'ABC',
      history: {
        push: jest.fn(),
      },
      showErrorNotification: jest.fn(),
      submitResetPassword: jest.fn(),
      submitResetPasswordRequest: jest.fn(),
    }
  })

  describe('when user wants to reset password', () => {
    beforeEach(() => {
      props.token = ''
    })

    it('should display one input with submit button to receive user email', () => {
      // given
      const store = configureStore({
        data: {
          users: [{ id: 'CMOI' }],
        },
      }).store

      // when
      const wrapper = mount(
        <Provider store={store}>
          <MemoryRouter>
            <LostPassword {...props} />
          </MemoryRouter>
        </Provider>
      )

      // then
      const emailInput = wrapper.find('input[type="email"]')
      expect(emailInput).toHaveLength(1)
      const submitButton = wrapper.find({ children: 'Envoyer' }).find('button')
      expect(submitButton).toHaveLength(1)
      expect(submitButton.prop('disabled')).toBe(true)
    })

    describe('when user start writing email', () => {
      it('submit button should not be disabled', () => {
        // given
        const store = configureStore({
          data: {
            users: [{ id: 'CMOI' }],
          },
        }).store

        // when
        const wrapper = mount(
          <Provider store={store}>
            <MemoryRouter>
              <LostPassword {...props} />
            </MemoryRouter>
          </Provider>
        )
        wrapper
          .find('input[type="email"]')
          .simulate('change', { target: { value: 'email' } })

        // then
        const submitButton = wrapper
          .find({ children: 'Envoyer' })
          .find('button')
        expect(submitButton.prop('disabled')).toBe(false)
      })
    })

    describe('when user successfully request password change', () => {
      it('should redirect success message page', () => {
        // when
        const wrapper = shallow(<LostPassword {...props} />)
        wrapper.instance().redirectToResetPasswordRequestSuccessPage()

        // then
        expect(props.history.push).toHaveBeenCalledWith(
          '/mot-de-passe-perdu?envoye=1'
        )
      })
    })

    describe('when user does not succeed to request password change', () => {
      it('should display error message', () => {
        // when
        const wrapper = shallow(<LostPassword {...props} />)
        wrapper.instance().displayPasswordResetRequestErrorMessage()

        // then
        expect(props.showErrorNotification).toHaveBeenCalledWith(
          'Un problème est survenu pendant la réinitialisation du mot de passe, veuillez réessayer plus tard.'
        )
      })
    })
  })

  describe('when user resets password', () => {
    beforeEach(() => {
      props.token = 'ABC'
    })

    it('should display one input with submit button to receive new user password', () => {
      // given
      const store = configureStore({
        data: {
          users: [{ id: 'CMOI' }],
        },
      }).store

      // when
      const wrapper = mount(
        <Provider store={store}>
          <MemoryRouter>
            <LostPassword {...props} />
          </MemoryRouter>
        </Provider>
      )

      // then
      const passwordInput = wrapper.find('input[type="password"]')
      expect(passwordInput).toHaveLength(1)
      const submitButton = wrapper
        .find('button')
        .findWhere(node => node.text() === 'Envoyer')
        .first()
      expect(submitButton).toHaveLength(1)
      expect(submitButton.props()['disabled']).toBe(true)
    })

    describe('when user starts writing password', () => {
      it('submit button should not be disabled', () => {
        // given
        const store = configureStore({
          data: {
            users: [{ id: 'CMOI' }],
          },
        }).store

        // when
        const wrapper = mount(
          <Provider store={store}>
            <MemoryRouter>
              <LostPassword {...props} />
            </MemoryRouter>
          </Provider>
        )
        wrapper
          .find('input[name="newPasswordValue"]')
          .simulate('change', { target: { value: 'password' } })

        // then
        const submitButton = wrapper
          .find({ children: 'Envoyer' })
          .find('button')
        expect(submitButton.prop('disabled')).toBe(false)
      })
    })

    describe('when user successfully change password', () => {
      it('should redirect success message page', () => {
        // when
        const wrapper = shallow(<LostPassword {...props} />)
        wrapper.instance().redirectToResetPasswordSuccessPage()

        // then
        expect(props.history.push).toHaveBeenCalledWith(
          '/mot-de-passe-perdu?change=1'
        )
      })
    })

    describe('when user does not succeed password change', () => {
      it('should display error message', () => {
        // given
        const action = {
          payload: {
            errors: {
              errorMessage: 'Server error',
            },
          },
        }
        const state = {}

        // when
        const wrapper = shallow(<LostPassword {...props} />)
        wrapper.instance().displayPasswordResetErrorMessages(state, action)

        // then
        expect(props.showErrorNotification).toHaveBeenCalledWith(
          "Une erreur s'est produite, veuillez réessayer ultérieurement."
        )
      })
    })
  })
})
