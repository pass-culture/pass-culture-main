import React from 'react'
import { shallow } from 'enzyme'

import Offerers from '../Offerers'

const dispatchMock = jest.fn()
const parseMock = () => ({ 'mots-cles': null })
const queryChangeMock = jest.fn()

describe('src | components | pages | Offerers', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        currentUser: {},
        dispatch: dispatchMock,
        offerers: [{ id: 'AE' }],
        pendingOfferers: [],
        pagination: {
          apiQuery: {
            keywords: null,
          },
        },
        query: {
          change: queryChangeMock,
          parse: parseMock,
        },
        location: {
          search: '',
        },
      }

      // when
      const wrapper = shallow(<Offerers {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('render', () => {
    describe('should pluralize offerers menu link', () => {
      it('should display Votre structure when one offerer', () => {
        // given
        const props = {
          currentUser: {},
          dispatch: dispatchMock,
          offerers: [{ id: 'AE' }],
          pendingOfferers: [],
          pagination: {
            apiQuery: {
              keywords: null,
            },
          },
          query: {
            change: queryChangeMock,
            parse: parseMock,
          },
          location: {
            search: '',
          },
        }

        // when
        const wrapper = shallow(<Offerers {...props} />)
        const heroSection = wrapper.find('HeroSection').props()

        // then

        expect(heroSection.title).toEqual('Votre structure juridique')
      })
      it('should display Vos structures when many offerers', () => {
        // given
        const props = {
          currentUser: {},
          dispatch: dispatchMock,
          offerers: [{ id: 'AE' }, { id: 'AF' }],
          pendingOfferers: [],
          pagination: {
            apiQuery: {
              keywords: null,
            },
          },
          query: {
            change: queryChangeMock,
            parse: parseMock,
          },
          location: {
            search: '',
          },
        }

        // when
        const wrapper = shallow(<Offerers {...props} />)
        const heroSection = wrapper.find('HeroSection').props()

        // then
        expect(heroSection.title).toEqual('Vos structures juridiques')
      })
    })
  })
})
