import React from 'react'
import { shallow } from 'enzyme'

import StocksManager from '../index'

describe('src | components | pages | Offer | StocksManager ', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialProps = {}

      // when
      const wrapper = shallow(<StocksManager {...initialProps} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
