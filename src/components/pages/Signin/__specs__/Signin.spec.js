import React from 'react'
import { shallow } from 'enzyme'
import Signin from '../Signin'

describe('src | components | pages | Signin | Signin ', () => {
  let dispatch
  let parse
  let props
  let action

  beforeEach(() => {
    action = {config: { method: 'POST' }}
    dispatch = jest.fn()
    parse = () => ({ 'mots-cles': null })

    props = {
      dispatch,
      query: {
        parse
      },
      history: {}
    }
  })

  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<Signin {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('handleSuccessRedirect', () => {

    describe('user is signed in for the first time, has no offer, has one virtual venue', () => {
      it('should redirect to offerers page', () => {
        // given
        action.payload = { datum: {
          hasOffers: false,
          hasPhysicalVenues: false
          }
        }
        const state = {}
        const wrapper = shallow(<Signin {...props} />)

        // when
        const result = wrapper.instance().handleSuccessRedirect(state, action)

        // then
        expect(result).toStrictEqual("/structures")
      })
    })

    describe('when the user has a digital offer and only a virtual venue', () => {
      it('should redirect to offerers page', () => {
        action.payload = { datum: {
          hasOffers: true,
          hasPhysicalVenues: false
          }
        }
        const state = {}
        const wrapper = shallow(<Signin {...props} />)

        // when
        const result = wrapper.instance().handleSuccessRedirect(state, action)

        // then
        expect(result).toStrictEqual("/structures")
      })
    })

    describe('when the user has no offers but a physical venue', () => {
      it('should redirect to offers page', () => {
        action.payload = { datum: {
          hasOffers: false,
          hasPhysicalVenues: true
          }
        }
        const state = {}
        const wrapper = shallow(<Signin {...props} />)

        // when
        const result = wrapper.instance().handleSuccessRedirect(state, action)

        // then
        expect(result).toStrictEqual("/offres")
      })
    })

    describe('when the user has offers in physical venues', () => {
      it('should redirect to offers page', () => {
        action.payload = { datum: {
          hasOffers: true,
          hasPhysicalVenues: true
          }
        }
        const state = {}
        const wrapper = shallow(<Signin {...props} />)

        // when
        const result = wrapper.instance().handleSuccessRedirect(state, action)

        // then
        expect(result).toStrictEqual("/offres")
      })
    })
  })
})
