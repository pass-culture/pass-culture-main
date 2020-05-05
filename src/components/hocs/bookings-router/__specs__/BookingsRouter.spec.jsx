import React from 'react'
import { shallow } from 'enzyme'

import BookingsRouter from '../BookingsRouter'
import BookingsContainer from '../../../pages/Bookings/BookingsContainer'
import BookingsContainerV2 from '../../../pages/Bookings-v2/BookingsRecapContainer'

describe('bookingsRouter', () => {
  describe('when Bookings-v2 feature flipping is active', () => {
    it('should load Bookings v2 component', () => {
      // given
      const props = {
        isBookingsV2Active: true,
      }

      // when
      const wrapper = shallow(<BookingsRouter {...props} />)

      // then
      expect(wrapper.find(BookingsContainerV2)).toHaveLength(1)
    })
  })

  describe('when Bookings v2 feature flipping is not active', () => {
    it('should load Bookings (v1) component', () => {
      // given
      const props = {
        isBookingsV2Active: false,
      }

      // when
      const wrapper = shallow(<BookingsRouter {...props} />)

      // then
      expect(wrapper.find(BookingsContainer)).toHaveLength(1)
    })
  })
})
