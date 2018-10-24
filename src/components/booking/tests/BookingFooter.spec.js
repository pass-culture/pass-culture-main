import React from 'react'
import { shallow } from 'enzyme'

import BookingFooter from '../BookingFooter'

describe('src | components | pages | search | BookingFooter', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        canSubmitForm: true,
        isBooked: true,
        isSubmitting: true,
        onCancel: jest.fn(),
        onSubmit: jest.fn(),
      }

      // when
      const wrapper = shallow(<BookingFooter {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
