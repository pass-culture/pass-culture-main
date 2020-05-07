import { shallow } from 'enzyme'
import React from 'react'

import MyInformationsField from '../MyInformationsField'

describe('my informations field', () => {
  const ERROR_MESSAGE = 'Vous devez renseigner au moins 3 caractères'

  it('should display error messages when there are validation errors', () => {
    // Given
    const secondErrorMessage = 'Vous ne devez pas renseigner plus de 10 caractères'
    const errors = [ERROR_MESSAGE, secondErrorMessage]

    // When
    const wrapper = shallow(
      <MyInformationsField
        errors={errors}
        label="input label"
        name="inputName"
      />
    )

    // Then
    const errorMessage = wrapper.find({ children: ERROR_MESSAGE })
    const otherErrorMessage = wrapper.find({ children: secondErrorMessage })
    expect(errorMessage).toHaveLength(1)
    expect(otherErrorMessage).toHaveLength(1)
  })

  it('should set aria-invalid to true on input field when there is validation error', () => {
    // Given
    const errors = [ERROR_MESSAGE]

    // When
    const wrapper = shallow(
      <MyInformationsField
        errors={errors}
        label="input label"
        name="inputName"
        value="MEFA"
      />
    )

    // Then
    const publicNameInput = wrapper.find("input[value='MEFA']")
    expect(publicNameInput.prop('aria-invalid')).toBe(true)
  })

  it('should not display error message when there is no validation error', () => {
    // Given
    const errors = null

    // When
    const wrapper = shallow(
      <MyInformationsField
        errors={errors}
        label="input label"
        name="inputName"
      />
    )

    // Then
    const errorMessage = wrapper.find({ children: ERROR_MESSAGE })
    expect(errorMessage).toHaveLength(0)
  })

  it('should set aria-invalid to false on input field when there is no validation error', () => {
    // Given
    const errors = null

    // When
    const wrapper = shallow(
      <MyInformationsField
        errors={errors}
        label="input label"
        name="inputName"
        value="MEFA"
      />
    )

    // Then
    const publicNameInput = wrapper.find("input[value='MEFA']")
    expect(publicNameInput.prop('aria-invalid')).toBe(false)
  })
})
