import { shallow } from 'enzyme'
import OffererCreationForm from '../OffererCreationForm'
import React from 'react'

describe('src | components | pages | OffererCreationForm', () => {
  it('should be clickable when values have been changed and are valid', () => {
    // given
    const props = {
      pristine: false,
      invalid: false,
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
    }

    // When
    const wrapper = shallow(<OffererCreationForm {...props} />)

    // Then
    expect(wrapper.find('button').prop('disabled')).toBe(true)
  })
})
