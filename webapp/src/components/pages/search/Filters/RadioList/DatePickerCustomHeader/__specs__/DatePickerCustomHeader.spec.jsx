import { shallow } from 'enzyme'
import React from 'react'
import { DatePickerCustomHeader } from '../DatePickerCustomHeader'

describe('components | DatePickerCustomHeader', () => {
  let props
  beforeEach(() => {
    props = {
      date: { toDate: jest.fn().mockReturnValue(new Date()) },
      decreaseMonth: jest.fn(),
      increaseMonth: jest.fn(),
      nextMonthButtonDisabled: false,
      prevMonthButtonDisabled: false,
    }
  })

  it('should go to previous month on back icon click', () => {
    // Given
    const wrapper = shallow(<DatePickerCustomHeader {...props} />)

    // When
    const previousMonthButton = wrapper
      .find('Icon[alt="Aller au mois précédent"]')
      .closest('button')
    previousMonthButton.simulate('click')

    // Then
    expect(props.decreaseMonth).toHaveBeenCalledTimes(1)
    expect(previousMonthButton.prop('disabled')).toBe(false)
    expect(previousMonthButton.find('Icon').prop('svg')).toBe('ico-back-black')
  })

  it('should disable buttons according to props', () => {
    // Given
    props.nextMonthButtonDisabled = true
    props.prevMonthButtonDisabled = true

    // When
    const wrapper = shallow(<DatePickerCustomHeader {...props} />)

    // Then
    const previousMonthButton = wrapper
      .find('Icon[alt="Aller au mois précédent"]')
      .closest('button')
    const nextMonthButton = wrapper.find('Icon[alt="Aller au mois suivant"]').closest('button')
    expect(previousMonthButton.prop('disabled')).toBe(true)
    expect(nextMonthButton.prop('disabled')).toBe(true)
  })

  it('should go to next month on next icon click', () => {
    // Given
    const props = {
      date: { toDate: jest.fn().mockReturnValue(new Date()) },
      decreaseMonth: jest.fn(),
      increaseMonth: jest.fn(),
      nextMonthButtonDisabled: false,
      prevMonthButtonDisabled: false,
    }
    const wrapper = shallow(<DatePickerCustomHeader {...props} />)

    // When
    const nextMonthButton = wrapper.find('Icon[alt="Aller au mois suivant"]').closest('button')
    nextMonthButton.simulate('click')

    // Then
    expect(props.increaseMonth).toHaveBeenCalledTimes(1)
    expect(nextMonthButton.prop('disabled')).toBe(false)
    expect(nextMonthButton.find('Icon').prop('svg')).toBe('ico-next-black')
  })

  it('should format date with full month and year', () => {
    // Given
    props.date = { toDate: jest.fn().mockReturnValue(new Date(2020, 3, 12)) }

    // When
    const wrapper = shallow(<DatePickerCustomHeader {...props} />)

    // Then
    const formattedDate = wrapper.find({ children: 'avril 2020' })
    expect(formattedDate).toHaveLength(1)
  })
})
