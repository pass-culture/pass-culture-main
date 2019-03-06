import React from 'react'
import { shallow } from 'enzyme'
import EventOccurrenceAndStockItem from '../index'

describe('src | components | pages | Offer | EventOccurrenceAndStockItem ', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialProps = {}

      // when
      const wrapper = shallow(<EventOccurrenceAndStockItem {...initialProps} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
