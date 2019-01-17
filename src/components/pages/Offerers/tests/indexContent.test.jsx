import React from 'react'
import { shallow } from 'enzyme'

import RawOfferers from '../RawIndex'

describe('src | components | pages | Offerers | IndexSearch', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        offerers: [{}],
        pendingOfferers: [],
        pagination: {
          apiQuery: {
            keywords: null,
          },
        },
      }

      // when
      const wrapper = shallow(<RawOfferers {...props} />)

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
          offerers: [{}],
          pendingOfferers: [],
          pagination: {
            apiQuery: {
              keywords: null,
            },
          },
        }

        // when
        const wrapper = shallow(<RawOfferers {...props} />)
        const heroSection = wrapper.find('HeroSection').props()

        // then

        expect(heroSection.title).toEqual('Votre structure juridique')
      })
      it('should display Vos structures when many offerers', () => {
        // given
        const props = {
          offerers: [{}, {}],
          pendingOfferers: [],
          pagination: {
            apiQuery: {
              keywords: null,
            },
          },
        }

        // when
        const wrapper = shallow(<RawOfferers {...props} />)
        const heroSection = wrapper.find('HeroSection').props()

        // then
        expect(heroSection.title).toEqual('Vos structures juridiques')
      })
    })
  })
})
