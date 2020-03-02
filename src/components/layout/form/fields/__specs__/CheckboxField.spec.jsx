import { mount } from 'enzyme'
import React from 'react'
import { Form } from 'react-final-form'

import CheckboxField from '../CheckboxField'

describe('components | CheckboxField', () => {
  it('should have input type checkbox', () => {
    // given
    const props = {
      id: 'checkbox-id',
      name: 'checkbox-name'
    }

    const formWithCheckboxField = ({handleSubmit}) => (
      <form>
        <CheckboxField {...props} />
        <button
          onClick={handleSubmit}
          type="submit"
        >
          {'Submit'}
        </button>
      </form>
    )

    // when
    const wrapper = mount(
      <Form
        onSubmit={jest.fn()}
        render={formWithCheckboxField}
      />
    )

    // then
    const input = wrapper.find('input')
    expect(input.prop('type')).toBe('checkbox')
    expect(input.prop('name')).toBe('checkbox-name')
    expect(input.prop('id')).toBe('checkbox-id')
  })

  it('should have label tag that has htmlFor prop to checkbox id when label is defined', () => {
    // given
    const props = {
      id: 'checkbox-id',
      name: 'checkbox-name',
      label: 'checkbox-label'
    }

    const formWithCheckboxField = ({handleSubmit}) => (
      <form>
        <CheckboxField {...props} />
        <button
          onClick={handleSubmit}
          type="submit"
        >
          {'Submit'}
        </button>
      </form>
    )

    // when
    const wrapper = mount(
      <Form
        onSubmit={jest.fn()}
        render={formWithCheckboxField}
      />
    )

    // then
    const label = wrapper.find('label')
    expect(label.prop('htmlFor')).toBe('checkbox-id')
  })
})
