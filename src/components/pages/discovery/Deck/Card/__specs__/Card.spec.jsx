import React from 'react'
import { shallow } from 'enzyme'

import Card from '../Card'

describe('src | components | pages | discovery | Deck | Card', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        handleClickRecommendation: jest.fn(),
        handleReadRecommendation: jest.fn(),
        match: { params: {} },
        position: 'position',
        width: 500,
      }

      // when
      const wrapper = shallow(<Card {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
  describe('render', () => {
    describe('background Color', () => {
      describe('when no color given in recommendation', () => {
        it('should render black by default', () => {
          // given
          const props = {
            handleClickRecommendation: jest.fn(),
            handleReadRecommendation: jest.fn(),
            match: { params: {} },
            position: 'position',
            width: 500,
          }

          // when
          const wrapper = shallow(<Card {...props} />)

          // then
          expect(wrapper.props().style.backgroundColor).toStrictEqual('black')
        })
      })

      describe('with a color given in recommendation', () => {
        it('should render associate color', () => {
          // given
          const props = {
            handleClickRecommendation: jest.fn(),
            handleReadRecommendation: jest.fn(),
            match: { params: {} },
            position: 'position',
            recommendation: {
              firstThumbDominantColor: [56, 28, 45],
            },
            width: 500,
          }

          // when
          const wrapper = shallow(<Card {...props} />)

          // then
          expect(wrapper.props().style.backgroundColor).toStrictEqual('hsl(324, 100%, 7.5%)')
        })
      })
    })
  })
})
