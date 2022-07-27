import '@testing-library/jest-dom'

import { fireEvent } from '@testing-library/dom'
import { render, screen } from '@testing-library/react'
import React from 'react'
import { Form } from 'react-final-form'

import CheckboxField from '../CheckboxField'

const renderCheckboxField = (props, initialValues) => {
  const renderForm = ({ handleSubmit }) => {
    return (
      <form>
        <CheckboxField {...props} />
        <button onClick={handleSubmit} type="submit">
          Submit
        </button>
      </form>
    )
  }

  return render(
    <Form
      initialValues={initialValues}
      onSubmit={jest.fn()}
      render={renderForm}
    />
  )
}

describe('components | CheckboxField', () => {
  let defaultProps = {
    id: 'checkbox-id',
    label: 'Checkbox label',
    name: 'checkbox-name',
  }

  let defaultInitialValues = {
    'checkbox-name': false,
  }

  it('should have input type checkbox', () => {
    const initialValues = { ...defaultInitialValues }
    const props = { ...defaultProps }
    renderCheckboxField(props, initialValues)

    const checkbox = screen.getByLabelText('Checkbox label')

    expect(checkbox).toBeInTheDocument()
    expect(checkbox.id).toStrictEqual(props.id)
    expect(checkbox.name).toStrictEqual(props.name)
    expect(checkbox.checked).toStrictEqual(initialValues[props.name])
    expect(checkbox.disabled).toBe(false)
  })

  it('should be unchecked', () => {
    const initialValues = {
      ...defaultInitialValues,
      'checkbox-name': false,
    }
    const props = { ...defaultProps }
    renderCheckboxField(props, initialValues)

    const checkbox = screen.getByLabelText('Checkbox label')

    expect(checkbox.checked).toStrictEqual(initialValues[props.name])
  })

  it('should be disabled', () => {
    const initialValues = { ...defaultInitialValues }
    const props = {
      ...defaultProps,
      disabled: true,
    }
    renderCheckboxField(props, initialValues)

    const checkbox = screen.getByLabelText('Checkbox label')

    expect(checkbox.disabled).toStrictEqual(props.disabled)
  })

  it('should change value on click', () => {
    const initialValues = { ...defaultInitialValues }
    const props = { ...defaultProps }
    renderCheckboxField(props, initialValues)

    const checkbox = screen.getByLabelText('Checkbox label')
    fireEvent.click(checkbox)

    expect(checkbox.checked).toStrictEqual(!initialValues[props.name])
  })
})
