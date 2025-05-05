import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { QuantityInput, QuantityInputProps } from './QuantityInput'

const renderQuantityInput = (props: QuantityInputProps) => {
  return render(<QuantityInput {...props} />)
}

const LABELS = {
  input: 'Quantité',
  checkbox: 'Illimité',
}

describe('QuantityInput', () => {
  it('should display an input and a checkbox', () => {
    renderQuantityInput({ label: LABELS.input })

    expect(
      screen.getByRole('spinbutton', { name: LABELS.input })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('checkbox', { name: LABELS.checkbox })
    ).toBeInTheDocument()
  })

  it('should display the checkbox disabled when the input is disabled', () => {
    renderQuantityInput({ label: LABELS.input, disabled: true })

    const input = screen.getByRole('spinbutton', { name: LABELS.input })
    expect(input).toBeDisabled()

    const checkbox = screen.getByRole('checkbox', { name: LABELS.checkbox })
    expect(checkbox).toBeDisabled()
  })

  it('should execute the onChange callback when the input value changes', async () => {
    const onChange = vi.fn()
    renderQuantityInput({ label: LABELS.input, onChange })

    const input = screen.getByRole('spinbutton', { name: LABELS.input })
    await userEvent.type(input, '1')
    expect(onChange.mock.calls.length).toBe(1)
  })

  it('should empty the input value when the checkbox is checked', async () => {
    const onChange = vi.fn()
    renderQuantityInput({ label: LABELS.input, onChange: onChange, value: 1 })

    const input = screen.getByRole('spinbutton', { name: LABELS.input })
    const checkbox = screen.getByRole('checkbox', { name: LABELS.checkbox })

    await userEvent.type(input, '1')
    expect(input).toHaveValue(1)

    await userEvent.click(checkbox)
    expect(onChange).toHaveBeenLastCalledWith(
      expect.objectContaining({
        target: expect.objectContaining({ value: '' }),
      })
    )
  })

  it('should uncheck the checkbox when the input value is set', async () => {
    renderQuantityInput({ label: LABELS.input, value: 1 })

    let input = screen.getByRole('spinbutton', { name: LABELS.input })
    let checkbox = screen.getByRole('checkbox', { name: LABELS.checkbox })

    await userEvent.type(input, '1')
    expect(input).toHaveValue(1)
    expect(checkbox).not.toBeChecked()
  })

  it('should check the checkbox when the input value is emptied manually', async () => {
    renderQuantityInput({ label: LABELS.input, value: 1 })

    const input = screen.getByRole('spinbutton', { name: LABELS.input })
    const checkbox = screen.getByRole('checkbox', { name: LABELS.checkbox })

    expect(input).toHaveValue(1)

    await userEvent.clear(input)
    expect(input).toHaveValue(null)
    expect(checkbox).toBeChecked()
  })

  it('should move focus to the input when the checkbox is unchecked', async () => {
    const minimum = 10
    renderQuantityInput({ label: LABELS.input, minimum, value: undefined })

    const input = screen.getByRole('spinbutton', { name: LABELS.input })
    const checkbox = screen.getByRole('checkbox', { name: LABELS.checkbox })

    await userEvent.click(checkbox)
    expect(checkbox).not.toBeChecked()
    expect(input).toHaveFocus()
  })
})
