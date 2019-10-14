import { shallow } from 'enzyme'
import React from 'react'

import VersoControls from '../VersoControls'

describe('src | components | layout | Verso | VersoControls | VersoControls', () => {
  describe('when the offer is not booked', () => {
    it('should render the wallet, the favorite button, the share button and the booking link', () => {
      // given
      const props = {
        isBooked: false,
      }

      // when
      const wrapper = shallow(<VersoControls {...props} />)

      // then
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('when the offer is booked', () => {
    it('should render the wallet, the favorite button, the share button and the cancelling link', () => {
      // given
      const props = {
        isBooked: true,
      }

      // when
      const wrapper = shallow(<VersoControls {...props} />)

      // then
      expect(wrapper).toMatchSnapshot()
    })
  })
})
