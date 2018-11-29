import React from 'react'
import { shallow } from 'enzyme'

import { RawDeckNavigation } from '../DeckNavigation'

describe('src | components | pages | discovery | RawDeckNavigation', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        height: 500,
        recommendation: {},
      }

      // when
      const wrapper = shallow(<RawDeckNavigation {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
  describe('render', () => {
    describe('Background Color', () => {
      describe('When no color given in recommendation', () => {
        it('should render black by default', () => {
          // given
          const props = {
            height: 500,
            recommendation: {},
          }

          // when
          const wrapper = shallow(<RawDeckNavigation {...props} />)

          // then
          expect(wrapper.props().style.background).toEqual(
            'linear-gradient(to bottom, rgba(0,0,0,0) 0%,black 30%,black 100%)'
          )
        })
      })

      describe('With a color given in recommendation', () => {
        it('should render associate color', () => {
          // given
          const props = {
            height: 500,
            recommendation: {
              firstThumbDominantColor: [56, 28, 45],
            },
          }

          // when
          const wrapper = shallow(<RawDeckNavigation {...props} />)

          // then
          expect(wrapper.props().style.background).toEqual(
            'linear-gradient(to bottom, rgba(0,0,0,0) 0%,hsl(324, 100%, 7.5%) 30%,hsl(324, 100%, 7.5%) 100%)'
          )
        })
      })
    })
  })
})
