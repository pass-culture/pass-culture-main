import React from 'react'
import { shallow } from 'enzyme'
import Signin from '../Signin'

describe('src | components | pages | Signin | Signin ', () => {
  const dispatch = jest.fn()
  const parse = jest.fn()

  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialProps = {
        query: {
          parse
        }
      }

      // when
      const wrapper = shallow(<Signin {...initialProps} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('handleSuccessRedirect', () => {
    describe('when the user is signin for the first time and has no offer and only a virtual venue created by default', () => {
      it('should redirect to offerers page', () => {
        // given
        const initialProps = {
          query: {
            parse: () => ({}),
          },
          dispatch: dispatch,
          history: {},
        }
        const action = {
          config: { method: 'POST' },
          payload: { datum: {
            hasOffers: false,
            hasPhysicalVenues: false
            }
          },
        }
        const state = {}

        // when
        const wrapper = shallow(<Signin {...initialProps} />)
        const result = wrapper.instance().handleSuccessRedirect(state, action)

        // then
        expect(result).toEqual("/structures")
      })
    })
    describe('when the user has a digital offer and only a virtual venue', () => {
      it('should redirect to offerers page', () => {
        // given
        const initialProps = {
          query: {
            parse: () => ({}),
          },
          dispatch: dispatch,
          history: {},
        }
        const action = {
          config: { method: 'POST' },
          payload: { datum: {
            hasOffers: true,
            hasPhysicalVenues: false
            }
          },
        }
        const state = {}


        // when
        const wrapper = shallow(<Signin {...initialProps} />)
        const result = wrapper.instance().handleSuccessRedirect(state, action)

        // then
        expect(result).toEqual("/structures")
      })
    })
    describe('when the user has no offers but a physical venue', () => {
      it('should redirect to offers page', () => {
        // given
        const initialProps = {
          query: {
            parse: () => ({}),
          },
          dispatch: dispatch,
          history: {},
        }
        const action = {
          config: { method: 'POST' },
          payload: {
            datum: {
              hasOffers: false,
              hasPhysicalVenues: true
            }
          }
        }
        const state = {}

        // when
        const wrapper = shallow(<Signin {...initialProps} />)
        const result = wrapper.instance().handleSuccessRedirect(state, action)

        // then
        expect(result).toEqual("/offres")
      })
    })
    describe('when the user has offers in  physical venues', () => {
      it('should redirect to offers page', () => {
        // given
        const initialProps = {
          query: {
            parse: () => ({}),
          },
          dispatch: dispatch,
          history: {},
        }
        const action = {
          config: { method: 'POST' },
          payload: {
            datum: {
              hasOffers: true,
              hasPhysicalVenues: true
            }
          },
        }
        const state = {}

        // when
        const wrapper = shallow(<Signin {...initialProps} />)
        const result = wrapper.instance().handleSuccessRedirect(state, action)

        // then
        expect(result).toEqual("/offres")
      })
    })
  })
})
