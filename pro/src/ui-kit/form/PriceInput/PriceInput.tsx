import React, { type ForwardedRef, useEffect, useRef, useState } from 'react'

import type { Currency } from '@/commons/core/shared/types'
import { Checkbox } from '@/design-system/Checkbox/Checkbox'
import {
  TextInput,
  type TextInputProps,
} from '@/design-system/TextInput/TextInput'

/**
 * Props for the PriceInput component.
 *
 * @extends Pick<TextInputProps, 'name' | 'max' | 'disabled'>
 */
export type PriceInputProps = Pick<
  TextInputProps,
  'name' | 'max' | 'disabled' | 'description'
> & {
  /**
   * A label for the input,
   * also used as the aria-label for the group.
   */
  label: string
  /**
   * The name of the input, mind what's being used in the form.
   */
  name?: string
  /**
   * A callback when the quantity changes.
   */
  onChange?: React.InputHTMLAttributes<HTMLInputElement>['onChange']
  /**
   * A callback when the quantity text input is blurred.
   */
  onBlur?: React.InputHTMLAttributes<HTMLInputElement>['onBlur']
  /**
   * The quantity value. Should be `undefined` if the quantity is unlimited.
   */
  value?: number | ''
  /**
   * A flag to show the "Gratuit" checkbox.
   */
  showFreeCheckbox?: boolean
  hideAsterisk?: boolean
  /**
   * A custom error message to be displayed.
   * If this prop is provided, the error message will be displayed and the field will be marked as errored
   */
  error?: string
  /**
   * Currency to use to display currency icon
   * @default EUR
   */
  currency?: Currency
  description?: string
}

/**
 * The PriceInput component is a combination of a TextInput and a Checkbox to define prices.
 * It integrates with Formik for form state management and is used when an null price is meant to be interpreted as free.
 *
 * ---
 *
 * @param {PriceInputProps} props - The props for the PriceInput component.
 * @returns {JSX.Element} The rendered PriceInput component.
 *
 * @example
 * <PriceInput
 *  label="Price"
 *  name="price"
 *  max={100}
 * />
 */
export const PriceInput = React.forwardRef(
  (
    {
      name,
      label,
      value,
      max,
      disabled,
      showFreeCheckbox,
      hideAsterisk = false,
      error,
      description,
      currency = 'EUR',
      onChange,
      onBlur,
    }: PriceInputProps,
    ref: ForwardedRef<HTMLInputElement>
  ) => {
    const priceRef = useRef<HTMLInputElement>(null)

    const freeName = `${name}.free`
    const freeRef = useRef<HTMLInputElement>(null)
    const initialIsFree = value === 0
    const [isFree, setIsFree] = useState(initialIsFree)

    const step = currency === 'XPF' ? 1 : 0.01

    const labelCurrency = currency === 'XPF' ? '(en F)' : '(en €)'

    useEffect(() => {
      // Move focus to the price input if free is unchecked.
      const focusedElement = document.activeElement as HTMLElement
      const isFreeCheckboxFocused = focusedElement === freeRef.current
      if (!isFree && isFreeCheckboxFocused) {
        priceRef.current?.focus()
      }
    }, [isFree])

    const onTextInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
      const newPriceAmount: string = event.target.value

      let cleanedPriceAmount =
        newPriceAmount !== '' ? Number(newPriceAmount) : undefined
      if (showFreeCheckbox && isFree) {
        cleanedPriceAmount = 0
      }

      onChange?.({
        target: { valueAsNumber: cleanedPriceAmount },
      } as React.ChangeEvent<HTMLInputElement>)

      showFreeCheckbox && setIsFree(event.target.value === '0')
    }

    const onCheckboxChange = () => {
      const nextIsFree = !isFree
      setIsFree(nextIsFree)

      let nextFieldValue = ''
      if (nextIsFree) {
        // If the checkbox is going to be checked,
        // we need to set the price to '0'
        // '0' means free offer.
        nextFieldValue = '0'
      }

      onChange?.({
        target: { valueAsNumber: Number(nextFieldValue) },
      } as React.ChangeEvent<HTMLInputElement>)
    }

    const inputExtension = (
      <Checkbox
        ref={freeRef}
        label="Gratuit"
        checked={isFree}
        name={freeName}
        onChange={onCheckboxChange}
        disabled={disabled}
      />
    )

    return (
      <div ref={ref}>
        <TextInput
          ref={priceRef}
          autoComplete="off"
          required={!hideAsterisk}
          name={name}
          label={`${label} ${labelCurrency}`}
          value={value?.toString() ?? ''}
          type="number"
          step={step}
          min={0}
          max={max}
          disabled={disabled}
          description={description}
          requiredIndicator={!hideAsterisk ? 'symbol' : null}
          onChange={onTextInputChange}
          onBlur={onBlur}
          onKeyDown={(event) => {
            // If the number input should have no decimal, prevent the user from typing "," or "."
            if (step === 1 && /[,.]/.test(event.key)) {
              event.preventDefault()
            }
          }}
          error={error}
          {...(showFreeCheckbox ? { extension: inputExtension } : {})}
        />
      </div>
    )
  }
)
