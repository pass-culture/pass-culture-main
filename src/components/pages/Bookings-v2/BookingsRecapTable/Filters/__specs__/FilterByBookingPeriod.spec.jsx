import moment from 'moment/moment'
import { shallow } from 'enzyme/build/index'
import FilterByBookingPeriod from '../FilterByBookingPeriod'
import React from 'react'
import { EMPTY_FILTER_VALUE } from '../Filters'

describe('components | FilterByBookingPeriod', () => {
  let props
  beforeEach(() => {
    props = {
      oldestBookingDate: '2020-02-05',
      onHandleBookingBeginningDateChange: jest.fn(),
      onHandleBookingEndingDateChange: jest.fn(),
      selectedBookingBeginningDate: EMPTY_FILTER_VALUE,
      selectedBookingEndingDate: EMPTY_FILTER_VALUE,
    }
  })

  it('should call on handleBookingBeginningDateChange', () => {
    // Given
    const selectedDate = moment('2020-05-20')
    const wrapper = shallow(<FilterByBookingPeriod {...props} />)
    const bookingBeginningDateInput = wrapper.find({ placeholderText: 'JJ/MM/AAAA' }).at(0)

    // When
    bookingBeginningDateInput.simulate('change', selectedDate)

    // Then
    expect(props.onHandleBookingBeginningDateChange).toHaveBeenCalledWith(selectedDate)
  })

  it('should call on handleBookingEndingDateChange', () => {
    // Given
    const selectedDate = moment('2020-05-20')
    const wrapper = shallow(<FilterByBookingPeriod {...props} />)
    const bookingEndingDateInput = wrapper.find({ placeholderText: 'JJ/MM/AAAA' }).at(1)

    // When
    bookingEndingDateInput.simulate('change', selectedDate)

    // Then
    expect(props.onHandleBookingEndingDateChange).toHaveBeenCalledWith(selectedDate)
  })

  it('should not allow to select booking beginning date superior to booking ending date value', async () => {
    // Given
    const selectedDate = '2020-04-03'
    props.selectedBookingEndingDate = selectedDate
    const wrapper = shallow(<FilterByBookingPeriod {...props} />)

    // When
    const bookingBeginningDateInput = wrapper.find({ placeholderText: 'JJ/MM/AAAA' }).at(0)

    // Then
    expect(bookingBeginningDateInput.prop('maxDate')).toStrictEqual(selectedDate)
  })

  it('should not allow to select booking ending date inferior to booking beginning date value', async () => {
    // Given
    const selectedDate = '2020-02-18'
    props.selectedBookingBeginningDate = selectedDate
    const wrapper = shallow(<FilterByBookingPeriod {...props} />)

    // When
    const bookingEndingDateInput = wrapper.find({ placeholderText: 'JJ/MM/AAAA' }).at(1)

    // Then
    expect(bookingEndingDateInput.prop('minDate')).toStrictEqual(selectedDate)
  })
})
