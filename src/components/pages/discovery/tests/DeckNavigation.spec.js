import React from 'react'
import { mount, shallow } from 'enzyme'

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

    it('should match snapshot with flipHandler', () => {
      // given
      const props = {
        flipHandler: jest.fn(),
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
    describe(`prix de l'offre`, () => {
      it('should equal Gratuit when offer price is 0', () => {
        // given
        const props = {
          flipHandler: jest.fn(),
          height: 500,
          isFinished: false,
          recommendation: {
            offer: {
              stocks: [{ available: null, price: 0 }],
            },
          },
        }
        // when
        const wrapper = mount(<RawDeckNavigation {...props} />)
        const element = wrapper.find('span#deck-navigation-offer-price')
        // then
        expect(element).toBeDefined()
        expect(element.text()).toStrictEqual('Gratuit')
      })
      it(`should equal '0 -> 12 €' when offer price range is [0, 12]`, () => {
        // given
        const props = {
          flipHandler: jest.fn(),
          height: 500,
          isFinished: false,
          recommendation: {
            offer: {
              stocks: [
                { available: null, price: 12 },
                { available: null, price: 0 },
              ],
            },
          },
        }
        // when
        const wrapper = mount(<RawDeckNavigation {...props} />)
        const element = wrapper.find('span#deck-navigation-offer-price')
        // then
        expect(element).toBeDefined()
        expect(element.text()).toStrictEqual('0 → 12 €')
      })
      it(`should equal '12 -> 56 €' when offer price range is [12, 56]`, () => {
        // given
        const props = {
          flipHandler: jest.fn(),
          height: 500,
          isFinished: false,
          recommendation: {
            offer: {
              stocks: [
                { available: null, price: 42 },
                { available: null, price: 12 },
                { available: null, price: 56 },
              ],
            },
          },
        }
        // when
        const wrapper = mount(<RawDeckNavigation {...props} />)
        const element = wrapper.find('span#deck-navigation-offer-price')
        // then
        expect(element).toBeDefined()
        expect(element.text()).toStrictEqual('12 → 56 €')
      })
    })

    describe('background Color', () => {
      describe('when no color given in recommendation', () => {
        it('should render black by default', () => {
          // given
          const props = {
            height: 500,
            recommendation: {},
          }

          // when
          const wrapper = shallow(<RawDeckNavigation {...props} />)

          // then
          expect(wrapper.props().style.background).toStrictEqual(
            'linear-gradient(to bottom, rgba(0,0,0,0) 0%,black 30%,black 100%)'
          )
        })
      })

      describe('with a color given in recommendation', () => {
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
          expect(wrapper.props().style.background).toStrictEqual(
            'linear-gradient(to bottom, rgba(0,0,0,0) 0%,hsl(324, 100%, 7.5%) 30%,hsl(324, 100%, 7.5%) 100%)'
          )
        })
      })
    })
  })
})
