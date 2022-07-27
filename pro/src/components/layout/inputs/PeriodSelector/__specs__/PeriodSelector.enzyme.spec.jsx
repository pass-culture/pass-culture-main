import { shallow } from 'enzyme'
import React from 'react'

import PeriodSelector from '../PeriodSelector'

describe('components | PeriodSelector', () => {
  let props
  beforeEach(() => {
    props = {
      changePeriodBeginningDateValue: jest.fn(),
      changePeriodEndingDateValue: jest.fn(),
      isDisabled: false,
      label: 'Fake Label',
      periodBeginningDate: undefined,
      periodEndingDate: undefined,
    }
  })

  it('should call on changePeriodBeginningDateValue', async () => {
    // Given
    const selectedDate = new Date('2020-05-20')
    const wrapper = shallow(<PeriodSelector {...props} />)
    const beginningDateInput = wrapper
      .find({ placeholderText: 'JJ/MM/AAAA' })
      .at(0)

    // When
    beginningDateInput.simulate('change', selectedDate)

    // Then
    expect(props.changePeriodBeginningDateValue).toHaveBeenCalledTimes(1)
  })

  it('should call on changePeriodEndingDateValue', async () => {
    // Given
    const selectedDate = new Date('2020-05-20')
    const wrapper = shallow(<PeriodSelector {...props} />)
    const endingDateInput = wrapper
      .find({ placeholderText: 'JJ/MM/AAAA' })
      .at(1)

    // When
    endingDateInput.simulate('change', selectedDate)

    // Then
    expect(props.changePeriodEndingDateValue).toHaveBeenCalledTimes(1)
  })

  it('should not allow to select beginning date superior to ending date value', async () => {
    // Given
    const selectedDate = new Date('2020-04-03')
    props.periodEndingDate = selectedDate
    const wrapper = shallow(<PeriodSelector {...props} />)

    // When
    const bookingBeginningDateInput = wrapper
      .find({ placeholderText: 'JJ/MM/AAAA' })
      .at(0)

    // Then
    expect(bookingBeginningDateInput.prop('maxDate')).toStrictEqual(
      selectedDate
    )
  })

  it('should not allow to select ending date inferior to beginning date value', async () => {
    // Given
    const selectedDate = new Date('2020-02-18')
    props.periodBeginningDate = selectedDate
    const wrapper = shallow(<PeriodSelector {...props} />)

    // When
    const bookingEndingDateInput = wrapper
      .find({ placeholderText: 'JJ/MM/AAAA' })
      .at(1)

    // Then
    expect(bookingEndingDateInput.prop('minDate')).toStrictEqual(selectedDate)
  })
})
