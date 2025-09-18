import React, { type ForwardedRef, useEffect, useRef, useState } from 'react'

import type { Currency } from '@/commons/core/shared/types'
import { Checkbox } from '@/design-system/Checkbox/Checkbox'
import strokeEuroIcon from '@/icons/stroke-euro.svg'
import strokeFrancIcon from '@/icons/stroke-franc.svg'
import {
  TextInput,
  type TextInputProps,
} from '@/ui-kit/form/TextInput/TextInput'

import styles from './PriceInput.module.scss'

/**
 * Props for the PriceInput component.
 *
 * @extends Pick<TextInputProps, 'name' | 'max' | 'rightIcon' | 'disabled' | 'smallLabel' | 'className'>
 */
export type PriceInputProps = Pick<
  TextInputProps,
  'name' | 'max' | 'rightIcon' | 'disabled' | 'smallLabel' | 'className'
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
 *  rightIcon={strokeEuroIcon}
 * />
 *
 * @accessibility
 * - **Labels**: Always provide a meaningful label using the `label` prop.
 */
export const PriceInput = React.forwardRef(
  (
    {
      className,
      name,
      label,
      value,
      max,
      rightIcon,
      disabled,
      smallLabel,
      showFreeCheckbox,
      hideAsterisk = false,
      error,
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

    const currencyIcon = currency === 'XPF' ? strokeFrancIcon : strokeEuroIcon
    const step = currency === 'XPF' ? 1 : 0.01
    const hasDecimal = currency === 'EUR'

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
          data-testid="input-price"
          className={className}
          labelClassName={smallLabel ? styles['input-layout-small-label'] : ''}
          required={!hideAsterisk}
          name={name}
          label={label}
          value={value ?? ''}
          type="number"
          step={step}
          hasDecimal={hasDecimal}
          min={0}
          max={max}
          rightIcon={rightIcon || currencyIcon}
          disabled={disabled}
          asterisk={!hideAsterisk}
          onChange={onTextInputChange}
          onBlur={onBlur}
          hasError={!!error}
          error={error}
          {...(showFreeCheckbox ? { InputExtension: inputExtension } : {})}
        />
      </div>
    )
  }
)

PriceInput.displayName = 'PriceInput'
