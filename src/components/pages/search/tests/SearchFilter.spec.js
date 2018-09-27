import React from 'react'
import { shallow } from 'enzyme'

import SearchFilter from '../SearchFilter'

describe('src | components | pages | search | SearchFilter', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        handleQueryParamsChange: jest.fn(),
        queryParams: {},
      }

      // when
      const wrapper = shallow(<SearchFilter {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
