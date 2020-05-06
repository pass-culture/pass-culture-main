import { shallow } from 'enzyme'
import React from 'react'
import Toggle from '../Toggle'

describe('components | Toggle', () => {
  let props

  beforeEach(() => {
    props = {
      checked: false,
      id: 'fake-id',
      name: 'fake-name',
      onChange: jest.fn()
    }
  })

  describe('render', () => {
    it('should render an input with the right props', () => {
      // when
      const wrapper = shallow(<Toggle {...props} />)

      // then
      const input = wrapper.find('input')
      expect(input).toHaveLength(1)
      expect(input.prop('checked')).toBe(props.checked)
      expect(input.prop('id')).toBe(props.id)
      expect(input.prop('name')).toBe(props.name)
      expect(input.prop('onChange')).toStrictEqual(props.onChange)
      expect(input.prop('type')).toBe('checkbox')
    })

    it('should render a label with the right props when input is checked', () => {
      // given
      props.checked = true

      // when
      const wrapper = shallow(<Toggle {...props} />)

      // then
      const label = wrapper.find('label')
      expect(label).toHaveLength(1)
      expect(label.prop('className')).toBe('ft-label-on')
      expect(label.prop('htmlFor')).toBe(props.id)
    })

    it('should render a label with the right props when input is not checked', () => {
      // given
      props.checked = false

      // when
      const wrapper = shallow(<Toggle {...props} />)

      // then
      const label = wrapper.find('label')
      expect(label).toHaveLength(1)
      expect(label.prop('className')).toBe('ft-label-off')
      expect(label.prop('htmlFor')).toBe(props.id)
    })
  })
})
