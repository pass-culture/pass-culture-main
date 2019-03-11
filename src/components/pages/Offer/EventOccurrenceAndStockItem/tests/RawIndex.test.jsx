import React from 'react'
import { shallow } from 'enzyme'

import RawEventOccurrenceAndStockItem from '../RawIndex'

const dispatchMock = jest.fn()

describe('src | components | pages | Offer | EventOccurrenceAndStockItem | RawEventOccurrenceAndStockItem ', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialProps = {
        dispatch: dispatchMock,
      }

      // when
      const wrapper = shallow(
        <RawEventOccurrenceAndStockItem {...initialProps} />
      )

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
