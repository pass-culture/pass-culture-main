import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Formik } from 'formik'

import { QuantityInput, QuantityInputProps } from './QuantityInput'

const renderQuantityInput = (props: QuantityInputProps) => {
  return render(
    <Formik initialValues={{ quantity: '' }} onSubmit={() => {}}>
      <QuantityInput {...props} />
    </Formik>
  )
}

const LABELS = {
  input: /Quantité/,
  checkbox: /Illimité/,
}

describe('QuantityInput', () => {
  it('should display an input and a checkbox', () => {
    renderQuantityInput({})

    expect(
      screen.getByRole('spinbutton', { name: LABELS.input })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('checkbox', { name: LABELS.checkbox })
    ).toBeInTheDocument()
  })

  it('should execute the onChange callback when the input value changes', async () => {
    const onChange = vi.fn()
    renderQuantityInput({ onChange })

    const input = screen.getByRole('spinbutton', { name: LABELS.input })
    await userEvent.type(input, '1')
    expect(onChange.mock.calls.length).toBe(1)
  })

  it('should empty the input value when the checkbox is checked', async () => {
    renderQuantityInput({})

    const input = screen.getByRole('spinbutton', { name: LABELS.input })
    const checkbox = screen.getByRole('checkbox', { name: LABELS.checkbox })

    await userEvent.type(input, '1')
    expect(input).toHaveValue(1)

    await userEvent.click(checkbox)
    expect(checkbox).toBeChecked()
    expect(input).toHaveValue(null)
  })

  it('should check the checkbox when the input value is emptied manually', async () => {
    renderQuantityInput({})

    const input = screen.getByRole('spinbutton', { name: LABELS.input })
    const checkbox = screen.getByRole('checkbox', { name: LABELS.checkbox })

    await userEvent.type(input, '1')
    expect(input).toHaveValue(1)

    await userEvent.clear(input)
    expect(input).toHaveValue(null)
    expect(checkbox).toBeChecked()
  })

  it('should move focus to the input when the checkbox is unchecked and init the input with 1', async () => {
    renderQuantityInput({})

    const input = screen.getByRole('spinbutton', { name: LABELS.input })
    const checkbox = screen.getByRole('checkbox', { name: LABELS.checkbox })

    await userEvent.click(checkbox)
    expect(checkbox).not.toBeChecked()
    expect(input).toHaveFocus()
    expect(input).toHaveValue(1)
  })
})
