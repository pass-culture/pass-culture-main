import React from 'react'
import { shallow } from 'enzyme'

import NavByOfferType from '../pages/search/NavByOfferType'

describe('src | components | pages | NavByOfferType', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        handleQueryParamsChange: jest.fn(),
        title: 'fake Title',
      }

      // when
      const wrapper = shallow(<NavByOfferType {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
