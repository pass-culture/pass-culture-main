import React from 'react'
import { shallow } from 'enzyme'

import SubmitAndCancelControl from '../index'

describe('src | components | pages | Offer | StocksManagerContainer | StockItem | SubmitAndCancelControl ', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialProps = {}

      // when
      const wrapper = shallow(<SubmitAndCancelControl {...initialProps} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
