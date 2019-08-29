import DatePickerCustomField from '../DatePickerCustomField'
import React from 'react'
import { shallow } from 'enzyme'

describe('src | components | forms | inputs | DatePickerField | DatePickerCustomField', () => {
  let props

  beforeEach(() => {
    props = {
      value: 'fake value',
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<DatePickerCustomField {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    it('should render a DatePickerCustomField with the proper css class when input value is not provided', () => {
      // given
      props.value = null

      // when
      const wrapper = shallow(<DatePickerCustomField {...props} />)

      // then
      expect(wrapper.prop('className')).toBe('react-datepicker__input-container_wrapper')
    })

    it('should render a DatePickerCustomField with the proper css class when input value is provided', () => {
      // when
      const wrapper = shallow(<DatePickerCustomField {...props} />)

      // then
      expect(wrapper.prop('className')).toBe('react-datepicker__input-container_wrapper selected')
    })

    it('should render a DatePickerCustomField with default props', () => {
      // when
      const wrapper = shallow(<DatePickerCustomField {...props} />)

      // then
      const input = wrapper.find('input')
      expect(input).toHaveLength(1)
      expect(input.props()).toStrictEqual({
        className: 'pc-final-form-datepicker-input',
        readOnly: true,
        value: 'fake value',
      })
    })
  })
})
