import React from 'react'
import { shallow } from 'enzyme'

import Bookings from '../Bookings'

describe('src | components | pages | Bookings', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<Bookings />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
