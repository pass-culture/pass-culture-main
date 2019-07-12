import React from 'react'
import { Form } from 'react-final-form'
import { render, shallow } from 'enzyme'

import HiddenField from '../HiddenField'

describe('src | components | forms | inputs | HiddenField', () => {
  it('should match snapshot with required props', () => {
    // given
    const props = { name: 'the-input-name' }

    // when
    const wrapper = shallow(<HiddenField {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })
  it('attributes should defined for a field of type hidden', () => {
    // given
    const props = {
      'any-native-input-prop': 'a value',
      id: 'the-input-id',
      name: 'the-input-name',
    }

    // when
    const wrapper = render(
      <Form
        onSubmit={jest.fn()}
        render={<HiddenField {...props} />}
      />
    )
    const inputElement = wrapper.find('#the-input-id')

    // then
    expect(inputElement).toHaveLength(1)
    expect(inputElement.prop('any-native-input-prop')).toStrictEqual('a value')
  })
})
