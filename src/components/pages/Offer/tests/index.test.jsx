import React from 'react'
import { shallow } from 'enzyme'
import OfferPage from '../index'

describe('src | components | pages | Offer | OfferPage ', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialProps = {}

      // when
      const wrapper = shallow(<OfferPage {...initialProps} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
