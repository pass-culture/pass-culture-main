// jest --env=jsdom ./src/components/verso/tests/VersoBookingButton --watch
import React from 'react'
import { shallow } from 'enzyme'

import VersoBookingButton, { getBookingName } from '../VersoBookingButton'

describe('src | components | verso | VersoBookingButton', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {}

      // when
      const wrapper = shallow(<VersoBookingButton {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
  describe('getBookingName', () => {
    it('should return booking name', () => {
      // given
      const booking = {
        stock: {
          resolvedOffer: {
            eventOrThing: {
              name: 'foo',
            },
          },
        },
      }
      // when
      const result = getBookingName(booking)
      // then
      expect(result).toBeDefined()
      expect(result).toBe('foo')
    })
  })
})
