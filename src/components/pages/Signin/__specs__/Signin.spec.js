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
    describe('when the user is signin for the first time and has no offer and only a virtual venue', () => {
      it('should redirect to offerer page', () => {
        // given
        const initialProps = {
          query: {
            parse: () => ({}),
          },
          dispatch: dispatch,
          history: {},
        }

        const wrapper = shallow(<Signin {...initialProps} />)

        // when
        const action = {
          config: { method: 'POST' },
          payload: { datum: {
            currentUser: {
              hasOffers: false,
              hasPhysicalVenues: false
            }
          } },
        }
        const state = {}
        const result = wrapper.instance().handleSuccessRedirect(state, action)

        // then
        expect(result).toEqual("/structures")
      })
    })

    describe('when the user is signin and has a digital offer and only a virtual venue', () => {
      it('should redirect to offers page', () => {
        // given
        const initialProps = {
          query: {
            parse: () => ({}),
          },
          dispatch: dispatch,
          history: {},
        }

        const wrapper = shallow(<Signin {...initialProps} />)

        // when
        const action = {
          config: { method: 'POST' },
          payload: { datum: {
            currentUser: {
              hasOffers: true,
              hasPhysicalVenues: false
            }
          }
        },
      }
      const state = {}
      const result = wrapper.instance().handleSuccessRedirect(state, action)

      // then
      expect(result).toEqual("/offres")
    })
  })

    describe('when the user is signin and has a digital offer and a physical venue', () => {
      it('should redirect to offers page', () => {
        // given
        const initialProps = {
          query: {
            parse: () => ({}),
          },
          dispatch: dispatch,
          history: {},
        }

        const wrapper = shallow(<Signin {...initialProps} />)

        // when
        const action = {
          config: { method: 'POST' },
          payload: { datum: {
            currentUser: {
              hasOffers: true,
              hasPhysicalVenues: true
            }
          }
        },
      }
      const state = {}
      const result = wrapper.instance().handleSuccessRedirect(state, action)

      // then
      expect(result).toEqual("/offres")
      })
    })
  })
})
