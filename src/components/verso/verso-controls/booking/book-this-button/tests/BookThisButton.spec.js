import React from 'react'
import { shallow } from 'enzyme'

import Price from '../../../../../layout/Price'
import BookThisButton, { formatOutputPrice } from '../../BookThisButton'

describe('src | components | verso | verso-buttons | BookThisButton', () => {
  describe('BookThisButton component', () => {
    it('should match snapshot with required props', () => {
      // given
      const props = {
        linkDestination: '/path/to/page/',
        priceValue: [0],
      }

      // when
      const wrapper = shallow(<BookThisButton {...props} />)
      const buttonLabel = wrapper.find('.button-label')

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
      expect(buttonLabel).toHaveLength(1)
      expect(buttonLabel.text()).toEqual("J'y vais!")
    })

    it('should contain a price elements', () => {
      // given
      const props = {
        linkDestination: '/path/to/page',
        priceValue: [0],
      }

      // when
      const wrapper = shallow(<BookThisButton {...props} />)
      const price = wrapper.find(Price)
      const splitter = wrapper.find('hr')

      // then
      expect(price).toHaveLength(1)
      expect(splitter).toHaveLength(1)
    })
  })

  describe('formatOutputPrice', () => {
    it('return a component with props', () => {
      // given
      const devise = '€'
      const values = [12, 22]

      // when
      const Component = () => formatOutputPrice(values, devise)
      const wrapper = shallow(<Component />)
      const props = wrapper.props()

      // then
      expect(props).toStrictEqual({
        devise: '€',
        endingPrice: 22,
        startingPrice: 12,
      })
    })
  })
})
