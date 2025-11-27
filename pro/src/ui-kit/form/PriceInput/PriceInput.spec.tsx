import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { useState } from 'react'
import { axe } from 'vitest-axe'

import type { Currency } from '@/commons/core/shared/types'

import { PriceInput, type PriceInputProps } from './PriceInput'

const renderPriceInput = (props: Partial<PriceInputProps>) => {
  const Wrapper = () => {
    const [value, setValue] = useState<number | null>(null)

    const onChange = (event: React.ChangeEvent<HTMLInputElement>) => {
      setValue(event.target.valueAsNumber)
    }

    return (
      <PriceInput
        {...props}
        name="price"
        label="Prix"
        value={value ?? ''}
        onChange={onChange}
      />
    )
  }

  return render(<Wrapper />)
}

const LABELS = {
  input: /Prix/,
  checkbox: /Gratuit/,
}

describe('PriceInput', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderPriceInput({})

    expect(
      //  Ingore the color contrast to avoid an axe-core error cf https://github.com/NickColley/jest-axe/issues/147
      await axe(container, {
        rules: { 'color-contrast': { enabled: false } },
      })
    ).toHaveNoViolations()
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
      expect(input).toHaveValue(0)
      expect(input).toHaveFocus()
    })
  })

  describe('Input validation', () => {
    const setNumberPriceValue = [
      { value: '20', expectedNumber: 20 },
      { value: 'azer', expectedNumber: null },
      { value: 'AZER', expectedNumber: null },
      { value: '2fsqjk', expectedNumber: 2 },
      { value: '2fsqm0', expectedNumber: 20 },
      { value: '20.50', expectedNumber: 20.5 },
      { value: '20.504', expectedNumber: 20.504 },
      { value: '20.5.2', expectedNumber: 20.52 },
    ]
    it.each(
      setNumberPriceValue
    )('should only type numbers for price input', async ({
      value,
      expectedNumber,
    }) => {
      renderPriceInput({})

      const input = screen.getByRole('spinbutton', { name: LABELS.input })
      await userEvent.type(input, value)
      await userEvent.tab()
      expect(input).toHaveValue(expectedNumber)
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

      expect(screen.getByText(`Prix (en ${sign})`)).toBeInTheDocument()
    })
  })
})
