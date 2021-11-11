import { shallow } from 'enzyme'
import React from 'react'

import BookingForm from '../BookingForm'

describe('src | components | layout | Booking | BookingForm', () => {
  let props
  beforeEach(() => {
    props = {
      className: 'fake className',
      decorators: [],
      formId: 'fake form id',
      initialValues: {},
      isEvent: true,
      isReadOnly: false,
      onFormSubmit: jest.fn(),
      onSetCanSubmitForm: jest.fn(),
    }
  })

  describe('render', () => {
    it('should render a BookingForm component with the right props', () => {
      // when
      const wrapper = shallow(<BookingForm {...props} />)

      // then
      expect(wrapper.props()).toStrictEqual({
        decorators: expect.any(Array),
        initialValues: {},
        onSubmit: props.onFormSubmit,
        render: expect.any(Function),
      })
    })
  })
})
