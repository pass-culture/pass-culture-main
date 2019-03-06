import React from 'react'
import { shallow } from 'enzyme'
import DateTimeForm from '../DateTimeForm'

describe('src | components | pages | Offer | EventOccurrenceAndStockItem | DateTimeForm', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialProps = {}

      // when
      const wrapper = shallow(<DateTimeForm {...initialProps} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
