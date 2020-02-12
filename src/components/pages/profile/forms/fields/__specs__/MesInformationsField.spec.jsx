import { shallow } from 'enzyme'
import React from 'react'
import { MesInformationsField } from '../MesInformationsField'

describe('src | components | pages | profile | MesInformations | MesInformationsField', () => {
  it('should display error message when there is validation errors', () => {
    // Given
    const errors = ['input validation error', 'another error']

    // When
    const wrapper = shallow(
      <MesInformationsField
        errors={errors}
        id="inputId"
        label="input label"
        name="inputName"
      />
    )

    // Then
    const errorMessage = wrapper.find({ children: 'input validation error' })
    const otherErrorMessage = wrapper.find({ children: 'another error' })
    expect(errorMessage).toHaveLength(1)
    expect(otherErrorMessage).toHaveLength(1)
  })

  it('should set aria-invalid to true on input field when there is validation errors', () => {
    // Given
    const errors = ['input validation error']

    // When
    const wrapper = shallow(
      <MesInformationsField
        errors={errors}
        id="inputId"
        label="input label"
        name="inputName"
      />
    )

    // Then
    const publicNameInput = wrapper.find("input[name='inputName']")
    expect(publicNameInput.props()['aria-invalid']).toBe(true)
  })

  it('should not display error message when there is no validation errors', () => {
    // Given
    const errors = null

    // When
    const wrapper = shallow(
      <MesInformationsField
        errors={errors}
        id="inputId"
        label="input label"
        name="inputName"
      />
    )

    // Then
    const errorMessage = wrapper.find({ children: 'input validation error' })
    expect(errorMessage).toHaveLength(0)
  })

  it('should set aria-invalid to false on input field when there is no validation errors', () => {
    // Given
    const errors = null

    // When
    const wrapper = shallow(
      <MesInformationsField
        errors={errors}
        id="inputId"
        label="input label"
        name="inputName"
      />
    )

    // Then
    const publicNameInput = wrapper.find("input[name='inputName']")
    expect(publicNameInput.props()['aria-invalid']).toBe(false)
  })
})
