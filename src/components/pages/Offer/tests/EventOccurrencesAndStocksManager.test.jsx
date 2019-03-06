import React from 'react'
import { shallow } from 'enzyme'
import EventOccurrencesAndStocksManager from '../index'

describe('src | components | pages | Offer | EventOccurrencesAndStocksManager ', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialProps = {}

      // when
      const wrapper = shallow(
        <EventOccurrencesAndStocksManager {...initialProps} />
      )

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
