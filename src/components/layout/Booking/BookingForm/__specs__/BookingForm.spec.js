import React from 'react'
import { shallow } from 'enzyme'

import BookingForm from '../BookingForm'

describe('src | components | layout | Booking | BookingForm', () => {
  let props

  beforeEach(() => {
    props = {
      className: 'fake className',
      formId: 'fake form id',
      initialValues: {},
      isEvent: true,
      isReadOnly: false,
      onMutation: jest.fn(),
      onSubmit: jest.fn()
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<BookingForm {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    it('should render a BookingForm component with the right props', () => {
      // when
      const wrapper = shallow(<BookingForm {...props} />)

      // then
      expect(wrapper.props()).toStrictEqual({
        decorators: expect.any(Array),
        initialValues: {},
        onSubmit: expect.any(Function),
        render: expect.any(Function)
      })
    })
  })
})
