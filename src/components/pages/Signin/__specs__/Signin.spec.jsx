import { shallow, mount } from 'enzyme'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import GenericError from 'components/layout/errors/GenericError'
import configureStore from 'store'

import Signin from '../Signin'

describe('src | components | pages | Signin | Signin', () => {
  let submit
  let props
  let action
  let store

  beforeEach(() => {
    submit = jest.fn()

    props = {
      submit,
      history: {
        push: jest.fn(),
      },
      isAccountCreationAvailable: true,
    }

    store = configureStore({
      data: {
        users: [{ id: 'CMOI' }],
      },
    }).store
  })

  it('should display 2 inputs and one link to account creation and one button to login', () => {
    // when
    const wrapper = mount(
      <Provider store={store}>
        <MemoryRouter>
          <Signin {...props} />
        </MemoryRouter>
      </Provider>
    )

    const emailInput = wrapper.find('input[type="email"]')
    const passwordInput = wrapper.find('input[type="password"]')
    const createAccountLink = wrapper.find({ children: 'Créer un compte' }).at(0)
    const signinButton = wrapper.find({ children: 'Se connecter' })

    //then
    expect(emailInput).toHaveLength(1)
    expect(passwordInput).toHaveLength(1)
    expect(createAccountLink).toHaveLength(1)
    expect(signinButton).toHaveLength(1)
  })

  describe('when user clicks on the eye on password input', () => {
    it('should reveal password', () => {
      // Given
      const wrapper = mount(
        <Provider store={store}>
          <MemoryRouter>
            <Signin {...props} />
          </MemoryRouter>
        </Provider>
      )
      const eyePasswordInput = wrapper.find('label').at(1).find('button')

      // When
      eyePasswordInput.invoke('onClick')({ preventDefault: jest.fn() })

      //then
      const passwordInput = wrapper.find('label').at(1).find('input')
      expect(passwordInput.prop('type')).toBe('text')
    })

    describe('when user re-click on eye', () => {
      it('should hide password', () => {
        // Given
        const wrapper = mount(
          <Provider store={store}>
            <MemoryRouter>
              <Signin {...props} />
            </MemoryRouter>
          </Provider>
        )
        const eyePasswordInput = wrapper.find('label').at(1).find('button')

        // When
        eyePasswordInput.invoke('onClick')({ preventDefault: jest.fn() })
        eyePasswordInput.invoke('onClick')({ preventDefault: jest.fn() })

        //then
        const passwordInput = wrapper.find('label').at(1).find('input')
        expect(passwordInput.prop('type')).toBe('password')
      })
    })
  })

  describe("when user clicks on 'Créer un compte'", () => {
    describe('when the API sirene is available', () => {
      it('should redirect to the creation page', () => {
        // when
        const wrapper = shallow(<Signin {...props} />)
        const createAccountLink = wrapper.find({ children: 'Créer un compte' })

        // then
        expect(createAccountLink.prop('to')).toStrictEqual('/inscription')
      })
    })

    describe('when the API sirene feature is disabled', () => {
      it('should redirect to the unavailable error page', () => {
        // given
        props.isAccountCreationAvailable = false

        // when
        const wrapper = mount(
          <Provider store={store}>
            <MemoryRouter>
              <Signin {...props} />
            </MemoryRouter>
          </Provider>
        )

        const createAccountLink = wrapper.find({ children: 'Créer un compte' }).at(0)

        // then
        expect(createAccountLink.prop('to')).toStrictEqual('/erreur/indisponible')
      })
    })
  })

  describe('when user clicks on "Se connecter"', () => {
    it('should call submit prop', () => {
      // Given
      const wrapper = mount(
        <Provider store={store}>
          <MemoryRouter>
            <Signin {...props} />
          </MemoryRouter>
        </Provider>
      )

      const emailInput = wrapper.find('input[type="email"]')
      emailInput.invoke('onChange')({ target: { value: 'un email' } })
      const passwordInput = wrapper.find('input[type="password"]')
      passwordInput.invoke('onChange')({ target: { value: 'un mot de passe' } })
      const submitButton = wrapper.find('form')

      // When
      submitButton.invoke('onSubmit')({ preventDefault: jest.fn() })

      // then
      expect(props.submit).toHaveBeenCalledWith(
        'un email',
        'un mot de passe',
        expect.any(Function),
        expect.any(Function)
      )
    })

    describe('when user is signed in for the first time, has no offer, has one virtual venue', () => {
      it('should redirect to offerers page', () => {
        // Given
        action = {
          payload: {
            datum: {
              hasOffers: true,
              hasPhysicalVenues: false,
            },
          },
        }
        const state = {}
        const wrapper = shallow(<Signin {...props} />)

        // when
        wrapper.instance().onHandleSuccessRedirect(state, action)

        // then
        expect(props.history.push).toHaveBeenCalledWith('/structures')
      })
    })

    describe('when the user has a digital offer and only a virtual venue', () => {
      it('should redirect to offerers page', () => {
        action.payload = {
          datum: {
            hasOffers: true,
            hasPhysicalVenues: false,
          },
        }
        const state = {}
        const wrapper = shallow(<Signin {...props} />)

        // when
        wrapper.instance().onHandleSuccessRedirect(state, action)

        // then
        expect(props.history.push).toHaveBeenCalledWith('/structures')
      })
    })

    describe('when the user has no offers but a physical venue', () => {
      it('should redirect to offers page', () => {
        action.payload = {
          datum: {
            hasOffers: false,
            hasPhysicalVenues: true,
          },
        }
        const state = {}
        const wrapper = shallow(<Signin {...props} />)

        // when
        wrapper.instance().onHandleSuccessRedirect(state, action)

        // then
        expect(props.history.push).toHaveBeenCalledWith('/offres')
      })
    })

    describe('when the user has offers in physical venues', () => {
      it('should redirect to offers page', () => {
        action.payload = {
          datum: {
            hasOffers: true,
            hasPhysicalVenues: true,
          },
        }
        const state = {}
        const wrapper = shallow(<Signin {...props} />)

        // when
        wrapper.instance().onHandleSuccessRedirect(state, action)

        // then
        expect(props.history.push).toHaveBeenCalledWith('/offres')
      })
    })

    describe('when login failed', () => {
      it('should display an error message', () => {
        const action = {
          payload: {
            errors: {
              password: 'erreur',
            },
          },
        }
        const state = {}
        const wrapper = shallow(<Signin {...props} />)

        // when
        wrapper.instance().onHandleFail(state, action)

        // then
        const genericError = wrapper.find(GenericError)
        expect(genericError.prop('message')).toBe('Identifiant ou mot de passe incorrect.')
      })
    })
  })
})
