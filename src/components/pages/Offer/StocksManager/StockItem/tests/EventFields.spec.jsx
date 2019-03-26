import React from 'react'
import { shallow } from 'enzyme'

import EventFields from '../EventFields'

describe('src | components | pages | Offer | StockItem | EventFields', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialProps = {
        beginningMinDate: '2019-03-29T01:56:55.610Z',
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
