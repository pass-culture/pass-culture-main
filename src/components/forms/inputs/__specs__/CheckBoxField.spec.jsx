import { shallow } from 'enzyme'
import React from 'react'
import { Field } from 'react-final-form'

import CheckBoxField from '../CheckBoxField'

describe('src | components | CheckBoxField', () => {
  it('should display a checkbox field', () => {
    // given
    const props = {
      children: <input type="checkbox" />,
      name: 'Fake name',
    }

    // when
    const wrapper = shallow(<CheckBoxField {...props} />)

    // then
    const field = wrapper.find(Field)
    expect(field.prop('name')).toBe('Fake name')
    expect(field.prop('render')).toStrictEqual(expect.any(Function))
    expect(field.prop('type')).toBe('checkbox')
    expect(field.prop('validate')).toStrictEqual(expect.any(Function))
  })
})
