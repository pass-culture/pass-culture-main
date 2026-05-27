import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { useState } from 'react'
import { vi } from 'vitest'
import { axe } from 'vitest-axe'

import type { Currency } from '@/commons/core/shared/types'

import { PriceInput, type PriceInputProps } from './PriceInput'

const renderPriceInput = (props: Partial<PriceInputProps>) => {
  const Wrapper = () => {
    const [value, setValue] = useState<number | string | null>(
      props.value ?? null
    )

    const onChange = (event: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = event.target.value
      if (newValue === '') {
        setValue(null)
      } else {
        const numValue = Number(newValue)
        setValue(Number.isNaN(numValue) ? null : numValue)
      }
      props.onChange?.(event)
    }

    return (
      <PriceInput
        {...props}
        name="price"
        label="Prix"
        value={value}
        onChange={onChange}
      />
    )
  }

  return render(<Wrapper />)
}

const LABELS = {
  input: /Prix \(en/,
  checkbox: /Gratuit/,
}

describe('PriceInput', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderPriceInput({})

    expect(await axe(container)).toHaveNoViolations()
  })

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

    it('should check the checkbox when initial value is 0', () => {
      renderPriceInput({ showFreeCheckbox: true, value: 0 })

      const checkbox = screen.getByRole('checkbox', { name: LABELS.checkbox })
      expect(checkbox).toBeChecked()
    })

    it('should disable input when initial value is 0', () => {
      renderPriceInput({ showFreeCheckbox: true, value: 0 })

      const input = screen.getByRole('spinbutton', { name: LABELS.input })
      expect(input).toBeDisabled()
    })

    it('should keep checkbox unchecked when initial value is non-zero', () => {
      renderPriceInput({ showFreeCheckbox: true, value: 10 })

      const checkbox = screen.getByRole('checkbox', { name: LABELS.checkbox })
      expect(checkbox).not.toBeChecked()
    })

    it('should trigger onChange when checkbox is clicked', async () => {
      const onChange = vi.fn()
      renderPriceInput({ showFreeCheckbox: true, onChange })

      const checkbox = screen.getByRole('checkbox', { name: LABELS.checkbox })
      await userEvent.click(checkbox)
      expect(onChange).toHaveBeenCalled()
    })

    it('should trigger onChange with empty string when checkbox is unchecked', async () => {
      const onChange = vi.fn()
      renderPriceInput({ showFreeCheckbox: true, value: 0, onChange })

      const checkbox = screen.getByRole('checkbox', { name: LABELS.checkbox })
      await userEvent.click(checkbox)
      expect(onChange).toHaveBeenCalled()
    })
  })

  describe('Input validation', () => {
    const setNumberPriceValue = [
      { value: '20', expected: '20' },
      { value: 'azer', expected: 'NaN' },
      { value: 'AZER', expected: 'NaN' },
      { value: '2fsqjk', expected: '2' },
      { value: '2fsqm0', expected: '20' },
      { value: '20.50', expected: '20.50' },
      { value: '20.504', expected: '20.504' },
      { value: '20.5.2', expected: '20.52' },
    ]
    it.each(
      setNumberPriceValue
    )('should only type numbers for price input', async ({
      value,
      expected,
    }) => {
      renderPriceInput({})

      const input = screen.getByRole('spinbutton', { name: LABELS.input })
      await userEvent.type(input, value)
      await userEvent.tab()
      const expectedValue = expected === '' ? null : Number(expected)
      const actualValue = (input as HTMLInputElement).valueAsNumber

      if (Number.isNaN(expectedValue as number)) {
        expect(Number.isNaN(actualValue)).toBe(true)
      } else {
        expect(actualValue).toBe(expectedValue)
      }
    })
  })

  describe('Currency', () => {
    const setCurrencyValue: Array<{ currency: Currency; sign: string }> = [
      { currency: 'EUR', sign: '€' },
      { currency: 'XPF', sign: 'F' },
    ]
    it.each(setCurrencyValue)(`should display the correct currency icon`, ({
      currency,
      sign,
    }) => {
      renderPriceInput({
        showFreeCheckbox: false,
        currency: currency,
      })

      expect(
        screen.getByText(new RegExp(`Prix \\(en ${sign}\\)`))
      ).toBeInTheDocument()
    })
  })
})
