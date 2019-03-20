import React from 'react'
import { shallow } from 'enzyme'

import EventFields from '../EventFields'

describe('src | components | pages | Offer | StockItem | EventFields', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialProps = {
        dispatch: jest.fn(),
        parseFormChild: jest.fn(),
      }

      // when
      const wrapper = shallow(<EventFields {...initialProps} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
