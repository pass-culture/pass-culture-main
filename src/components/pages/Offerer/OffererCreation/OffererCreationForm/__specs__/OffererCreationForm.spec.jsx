import { shallow } from 'enzyme'
import React from 'react'

import OffererCreationForm from '../OffererCreationForm'

describe('src | components | pages | OffererCreationForm', () => {
  it('should be clickable when values have been changed and are valid', () => {
    // given
    const props = {
      pristine: false,
      invalid: false,
      handleSubmit: () => {},
    }

    // When
    const wrapper = shallow(<OffererCreationForm {...props} />)

    // Then
    expect(wrapper.find('button').prop('disabled')).toBe(false)
  })

  it('should not be clickable when form is invalid', () => {
    // given
    const props = {
      pristine: false,
      invalid: true,
      handleSubmit: () => {},
    }

    // When
    const wrapper = shallow(<OffererCreationForm {...props} />)

    // Then
    expect(wrapper.find('button').prop('disabled')).toBe(true)
  })

  it('should not be clickable when values have not been changed', () => {
    // given
    const props = {
      pristine: true,
      invalid: false,
      handleSubmit: () => {},
    }

    // When
    const wrapper = shallow(<OffererCreationForm {...props} />)

    // Then
    expect(wrapper.find('button').prop('disabled')).toBe(true)
  })
})
