import React from 'react'
import { shallow } from 'enzyme'
import BookingDatePickerField from '../BookingDatePickerField'

describe('src | components | layout | Booking | BookingForm | BookingFormContent | BookingDatePickerField', () => {
  let fieldParams
  let handleChange
  let values

  beforeEach(() => {
    fieldParams = {
      input: {
        value: {
          date: '2019-01-01'
        }
      }
    }
    handleChange = jest.fn()
    values = {
      bookables: [],
      date: '2019-01-01',
      price: 12
    }
  })

  it('should match snapshot', () => {
    // when
    const MyComponent = BookingDatePickerField(handleChange, values)
    const wrapper = shallow(<MyComponent {...fieldParams} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
