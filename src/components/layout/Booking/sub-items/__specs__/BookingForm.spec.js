import React from 'react'
import { shallow } from 'enzyme'

import BookingForm from '../BookingForm'

describe('src | components | pages | search | BookingForm', () => {
  describe('snapshot', () => {
    it('should match the snapshot', () => {
      // given
      const props = {
        disabled: false,
        formId: 'super-form-id',
        onMutation: () => {},
        onSubmit: () => {},
      }

      // when
      const wrapper = shallow(<BookingForm {...props} />)

      // then
      expect(wrapper).toMatchSnapshot()
    })

    it('should match the snapshot when is read-only', () => {
      // given
      const props = {
        disabled: false,
        formId: 'super-form-id',
        isReadOnly: true,
        onMutation: () => {},
        onSubmit: () => {},
      }

      // when
      const wrapper = shallow(<BookingForm {...props} />)

      // then
      expect(wrapper).toMatchSnapshot()
    })
  })
})
