import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { PriceInput, PriceInputProps } from './PriceInput'

const renderPriceInput = (props: Partial<PriceInputProps>) => {
  return render(<PriceInput {...props} name="price" label="Prix" />)
}

const LABELS = {
  input: /Prix/,
  checkbox: /Gratuit/,
}

describe('PriceInput', () => {
  it('should display always display an input', () => {
    renderPriceInput({})

    expect(
      screen.getByRole('spinbutton', { name: LABELS.input })
    ).toBeInTheDocument()
  })

  describe('when "Gratuit" checkbox display is enabled', () => {
    it('should display a checkbox', () => {
      renderPriceInput({ showFreeCheckbox: true })

      expect(
        screen.getByRole('checkbox', { name: LABELS.checkbox })
      ).toBeInTheDocument()
    })

    it('should display the checkbox disabled when the input is disabled', () => {
      renderPriceInput({ showFreeCheckbox: true, disabled: true })

      const input = screen.getByRole('spinbutton', { name: LABELS.input })
      expect(input).toBeDisabled()

      const checkbox = screen.getByRole('checkbox', { name: LABELS.checkbox })
      expect(checkbox).toBeDisabled()
    })

    it('should check the checkbox when the input value changes to 0', async () => {
      renderPriceInput({ showFreeCheckbox: true })

      const input = screen.getByRole('spinbutton', { name: LABELS.input })
      const checkbox = screen.getByRole('checkbox', { name: LABELS.checkbox })

      await userEvent.clear(input)
      await userEvent.type(input, '0')
      expect(checkbox).toBeChecked()
    })

    it('should uncheck the checkbox when the input value changes to a non-zero value', async () => {
      renderPriceInput({ showFreeCheckbox: true })

      const input = screen.getByRole('spinbutton', { name: LABELS.input })
      const checkbox = screen.getByRole('checkbox', { name: LABELS.checkbox })

      await userEvent.type(input, '1')
      expect(checkbox).not.toBeChecked()
    })

    it('should set the input value to 0 when the checkbox is checked', async () => {
      renderPriceInput({ showFreeCheckbox: true })

      const input = screen.getByRole('spinbutton', { name: LABELS.input })
      const checkbox = screen.getByRole('checkbox', { name: LABELS.checkbox })

      await userEvent.click(checkbox)
      expect(input).toHaveValue(0)
    })

    it('should move focus to the input when the checkbox is unchecked and reset the input value', async () => {
      renderPriceInput({ showFreeCheckbox: true })

      const input = screen.getByRole('spinbutton', { name: LABELS.input })
      const checkbox = screen.getByRole('checkbox', { name: LABELS.checkbox })

      await userEvent.click(checkbox)
      await userEvent.click(checkbox)
      expect(input).toHaveValue(null)
      expect(input).toHaveFocus()
    })
  })
})
