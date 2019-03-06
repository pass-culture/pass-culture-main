import React from 'react'
import { shallow } from 'enzyme'
import DeleteDialog from '../DeleteDialog'

describe('src | components | pages | Offer | EventOccurrenceAndStockItem | DeleteDialog', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialProps = {}

      // when
      const wrapper = shallow(<DeleteDialog {...initialProps} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
