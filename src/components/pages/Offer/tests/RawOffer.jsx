import React from 'react'
import { shallow } from 'enzyme'

import RawOffer from '../RawOffer'

describe('src | components | pages | Offer | RawOffer ', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialProps = {}

      // when
      const wrapper = shallow(<RawOffer {...initialProps} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
