// jest ./src/components/booking/utils/tests/BookingForm --watch
import React from 'react'
import { shallow } from 'enzyme'

import BookingForm from '../BookingForm'

describe('src | components | pages | search | BookingForm', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      const props = {
        disabled: false,
        formId: 'super-form-id',
        onMutation: () => {},
        onSubmit: () => {},
      }
      const wrapper = shallow(<BookingForm {...props} />)
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
