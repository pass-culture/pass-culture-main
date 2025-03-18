import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'

import { QuantityInput, QuantityInputProps } from './QuantityInput'

type WrapperFormValues = { quantity: string }
type FormWrapperProps = Partial<QuantityInputProps & { initialQuantity?: string }>
const FormWrapper = (props: FormWrapperProps) => {
  const hookForm = useForm<WrapperFormValues>({
    defaultValues: {
      quantity: props.initialQuantity ?? '',
    },
  })

  const { register } = hookForm

  return <FormProvider {...hookForm}>
    <QuantityInput
      label="Quantité"
      {...register('quantity')}
      {...props}
    />
  </FormProvider>
}

const renderQuantityInput = (props: FormWrapperProps) => {
  render(<FormWrapper {...props} />)
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

  it('should display the checkbox disabled when the input is disabled', () => {
    renderQuantityInput({ disabled: true })

    const input = screen.getByRole('spinbutton', { name: LABELS.input })
    expect(input).toBeDisabled()

    const checkbox = screen.getByRole('checkbox', { name: LABELS.checkbox })
    expect(checkbox).toBeDisabled()
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

  it('should check the checkbox initially when the input value is an empty string', () => {
    renderQuantityInput({ initialQuantity: '' })

    let input = screen.getByRole('spinbutton', { name: LABELS.input })
    let checkbox = screen.getByRole('checkbox', { name: LABELS.checkbox })

    expect(input).toHaveValue(null)
    expect(checkbox).toBeChecked()
  })

  it('should uncheck the checkbox when the input value is set', () => {
    renderQuantityInput({ initialQuantity: '1' })

    let input = screen.getByRole('spinbutton', { name: LABELS.input })
    let checkbox = screen.getByRole('checkbox', { name: LABELS.checkbox })

    expect(input).toHaveValue(1)
    expect(checkbox).not.toBeChecked()
  })

  it('should move focus to the input when the checkbox is unchecked and init the input with the minimum', async () => {
    const min = 10
    renderQuantityInput({ min })

    const input = screen.getByRole('spinbutton', { name: LABELS.input })
    const checkbox = screen.getByRole('checkbox', { name: LABELS.checkbox })

    await userEvent.click(checkbox)
    expect(checkbox).not.toBeChecked()
    expect(input).toHaveFocus()
    expect(input).toHaveValue(min)
  })
})
