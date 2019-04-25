import React from 'react'
import { shallow } from 'enzyme'
import NoBookingView from '../NoBookingView'

describe('src | components | pages | my-bookings | NoBookingView', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<NoBookingView />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
