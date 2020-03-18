import { shallow } from 'enzyme'
import FilterCheckbox from '../FilterCheckbox'
import React from 'react'
import Icon from '../../../../../layout/Icon/Icon'

describe('components | FilterCheckbox', () => {
  let props

  beforeEach(() => {
    props = {
      className: 'my-classname',
      checked: false,
      id: 'my-id',
      label: 'my-label',
      name: 'my-name',
      onChange: jest.fn()
    }
  })

  describe('render', () => {
    it('should render an input with the right props', () => {
      // when
      const wrapper = shallow(<FilterCheckbox {...props} />)

      // then
      const input = wrapper.find('input')
      expect(input).toHaveLength(1)
      expect(input.prop('checked')).toBe(props.checked)
      expect(input.prop('id')).toBe(props.id)
      expect(input.prop('name')).toBe(props.name)
      expect(input.prop('onChange')).toStrictEqual(props.onChange)
      expect(input.prop('type')).toBe('checkbox')
    })

    it('should render a label with the right props', () => {
      // when
      const wrapper = shallow(<FilterCheckbox {...props} />)

      // then
      const label = wrapper.find('label')
      expect(label).toHaveLength(1)
      expect(label.prop('className')).toBe(props.className)
      expect(label.prop('htmlFor')).toBe(props.id)
      expect(label.text()).toBe('my-label')
    })

    describe('icon checked', () => {
      it('should be displayed when checkbox is checked', () => {
        // given
        props.checked = true

        // when
        const wrapper = shallow(<FilterCheckbox {...props} />)

        // then
        const icon = wrapper.find(Icon)
        expect(icon).toHaveLength(1)
        expect(icon.prop('className')).toBe('fc-icon-check')
        expect(icon.prop('svg')).toBe('ico-check-pink')
      })

      it('should not be displayed when checkbox is unchecked', () => {
        // given
        props.checked = false

        // when
        const wrapper = shallow(<FilterCheckbox {...props} />)

        // then
        const icon = wrapper.find(Icon)
        expect(icon).toHaveLength(0)
      })
    })
  })
})
