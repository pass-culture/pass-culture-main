import React, { type ForwardedRef, useRef } from 'react'

import type { Currency } from '@/commons/core/shared/types'
import { Checkbox } from '@/design-system/Checkbox/Checkbox'
import type { RequiredIndicator } from '@/design-system/common/types'
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
  'name' | 'max' | 'disabled' | 'description' | 'required'
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
  value?: number | string | null
  /**
   * A flag to show the "Gratuit" checkbox.
   */
  showFreeCheckbox?: boolean
  /** What type of required indicator is displayed */
  requiredIndicator?: RequiredIndicator
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
      disabled,
      requiredIndicator = 'symbol',
      required = true,
      error,
      max,
      description,
      currency = 'EUR',
      value,
      showFreeCheckbox,
      onChange,
      onBlur,
    }: PriceInputProps,
    ref: ForwardedRef<HTMLInputElement>
  ) => {
    const freeRef = useRef<HTMLInputElement>(null)
    const freeName = `${name}.free`

    const isFree = value === 0 || value === '0'
    const step = currency === 'XPF' ? 1 : 0.01
    const labelCurrency = currency === 'XPF' ? '(en F)' : '(en €)'

    const onCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const nextIsFree = e.target.checked
      const nextFieldValue = nextIsFree ? 0 : ''

      onChange?.({
        ...e,
        target: { ...e.target, name, value: nextFieldValue },
      } as unknown as React.ChangeEvent<HTMLInputElement>)
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
      <TextInput
        key={String(isFree)}
        ref={ref}
        name={name}
        disabled={disabled || isFree}
        label={`${label} ${labelCurrency}`}
        error={error}
        step={step}
        min={0}
        max={max}
        type="number"
        required={required}
        description={description}
        requiredIndicator={requiredIndicator}
        autoComplete="off"
        onChange={onChange}
        onBlur={onBlur}
        onKeyDown={(event) => {
          if (step === 1 && /[,.]/.test(event.key)) {
            event.preventDefault()
          }
        }}
        {...(showFreeCheckbox ? { extension: inputExtension } : {})}
      />
    )
  }
)
