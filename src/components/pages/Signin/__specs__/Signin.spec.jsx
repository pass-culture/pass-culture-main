import React from 'react'
import { shallow } from 'enzyme'
import Signin from '../Signin'
import { NavLink } from 'react-router-dom'

describe('src | components | pages | Signin | Signin ', () => {
  let dispatch
  let parse
  let props
  let action

  beforeEach(() => {
    action = { config: { method: 'POST' } }
    dispatch = jest.fn()
    parse = () => ({ 'mots-cles': null })

    props = {
      dispatch,
      errors: 'errors',
      query: {
        parse,
      },
      history: {},
      isAccountCreationAvailable: true,
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<Signin {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    describe('when the create a new account', () => {
      describe('when the API sirene is available', () => {
        it('should redirect to the creation page', () => {
          // when
          const wrapper = shallow(<Signin {...props} />)
          const createAccountLink = wrapper.find(NavLink)

          // then
          expect(createAccountLink.prop('to')).toStrictEqual('/inscription')
        })
      })

      describe('when the API sirene feature is disabled', () => {
        it('should redirect to the unavailable error page', () => {
          // given
          props.isAccountCreationAvailable = false

          // when
          const wrapper = shallow(<Signin {...props} />)
          const createAccountLink = wrapper.find(NavLink)

          // then
          expect(createAccountLink.prop('to')).toStrictEqual('/erreur/indisponible')
        })
      })
    })
  })

  describe('handleSuccessRedirect()', () => {
    describe('user is signed in for the first time, has no offer, has one virtual venue', () => {
      it('should redirect to offerers page', () => {
        // given
        action.payload = {
          datum: {
            hasOffers: false,
            hasPhysicalVenues: false,
          },
        }
        const state = {}
        const wrapper = shallow(<Signin {...props} />)

        // when
        const result = wrapper.instance().onHandleSuccessRedirect(state, action)

        // then
        expect(result).toStrictEqual('/structures')
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
        const result = wrapper.instance().onHandleSuccessRedirect(state, action)

        // then
        expect(result).toStrictEqual('/structures')
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
        const result = wrapper.instance().onHandleSuccessRedirect(state, action)

        // then
        expect(result).toStrictEqual('/offres')
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
        const result = wrapper.instance().onHandleSuccessRedirect(state, action)

        // then
        expect(result).toStrictEqual('/offres')
      })
    })
  })
})
