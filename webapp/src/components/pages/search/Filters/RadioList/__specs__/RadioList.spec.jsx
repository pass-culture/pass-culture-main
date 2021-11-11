import { mount, shallow } from 'enzyme'
import React from 'react'
import { DatePickerCustomHeader } from '../DatePickerCustomHeader/DatePickerCustomHeader'
import { RadioList } from '../RadioList'

describe('components | RadioList', () => {
  let props
  beforeEach(() => {
    props = {
      date: { option: 'today', selectedDate: new Date() },
      onDateSelection: jest.fn(),
      onPickedDate: jest.fn(),
    }
  })

  it('should render a list of date filters', () => {
    // When
    const wrapper = mount(<RadioList {...props} />)

    // Then
    const today = wrapper.find({ children: "Aujourd'hui" })
    const thisWeek = wrapper.find({ children: 'Cette semaine' })
    const thisWeekend = wrapper.find({ children: 'Ce week-end' })
    const exactDate = wrapper.find({ children: 'Date précise' })

    expect(today).toHaveLength(1)
    expect(thisWeek).toHaveLength(1)
    expect(thisWeekend).toHaveLength(1)
    expect(exactDate).toHaveLength(1)
  })

  it('should not render datepicker when filter date option is not "picked"', () => {
    // when
    const wrapper = shallow(<RadioList {...props} />)

    // then
    const datepicker = wrapper.find('DatePicker')
    expect(datepicker).toHaveLength(0)
  })

  it('should render datepicker when filter date option is "picked"', () => {
    // given
    props.date.option = 'picked'

    // when
    const wrapper = shallow(<RadioList {...props} />)

    // then
    const datepicker = wrapper.find('DatePicker')
    expect(datepicker).toHaveLength(1)
    expect(datepicker.prop('inline')).toBeDefined()
    expect(datepicker.prop('minDate')).toBeDefined()
    expect(datepicker.prop('onChange')).toBe(props.onPickedDate)
    expect(datepicker.prop('renderCustomHeader')).toBe(DatePickerCustomHeader)
    expect(datepicker.prop('selected')).toBeDefined()
  })

  it('should render check icon when date filter is selected', () => {
    // given
    props.date.option = 'currentWeekEnd'

    // when
    const wrapper = mount(<RadioList {...props} />)

    // then
    const checkedIconAfterSelection = wrapper.find('label[htmlFor="current-week-end"]+Icon')
    expect(checkedIconAfterSelection).toHaveLength(1)
  })

  it('should execute onDateSelection from props when date option is selected', () => {
    // given
    const wrapper = mount(<RadioList {...props} />)

    // when
    const currentWeekEndRadioButton = wrapper
      .find({ children: 'Ce week-end' })
      .closest('li')
      .find('input[type="radio"]')
    currentWeekEndRadioButton.simulate('change', { target: { value: 'currentWeekEnd' } })

    // then
    expect(props.onDateSelection).toHaveBeenCalledTimes(1)
  })
})
