import React from 'react'
import { shallow } from 'enzyme'

import Navigation from '../Navigation'

describe('src | components | pages | discovery | Deck | Navigation', () => {
  describe('snapshot', () => {
    it('should match the snapshot', () => {
      // given
      const props = {
        distanceClue: '',
        flipHandler: jest.fn(),
        height: 500,
        priceRange: [],
        separator: '-',
        trackConsultOffer: jest.fn(),
      }

      // when
      const wrapper = shallow(<Navigation {...props} />)

      // then
      expect(wrapper).toMatchSnapshot()
    })
  })
})
