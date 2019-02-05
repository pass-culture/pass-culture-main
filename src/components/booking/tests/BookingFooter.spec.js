// jest --env=jsdom ./src/components/booking/tests/BookingFooter --watch
import React from 'react'
import { shallow } from 'enzyme'

import BookingFooter from '../BookingFooter'

const onCancelMock = jest.fn()
const onSubmitMock = jest.fn()

describe('src | components | pages | search | BookingFooter', () => {
  describe('snapshot', () => {
    it('can not submit, is not booked, is not submitting', () => {
      // given
      const props = {
        canSubmitForm: false,
        isBooked: false,
        isSubmitting: false,
        onCancel: onCancelMock,
        onSubmit: onSubmitMock,
      }

      // when
      const wrapper = shallow(<BookingFooter {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
