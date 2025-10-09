import { useEffect, useRef, useState } from 'react'

import { Checkbox } from '@/design-system/Checkbox/Checkbox'
import {
  TextInput,
  type TextInputProps,
} from '@/design-system/TextInput/TextInput'

export type QuantityInputProps = Pick<
  TextInputProps,
  'disabled' | 'required' | 'requiredIndicator'
> & {
  /**
   * A label for the text input.
   */
  label?: string
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
  value?: number | null
  /**
   * The minimum value allowed for the quantity. Make sure it matches validation schema.
   */
  min?: number
  /**
   * The maximum value allowed for the quantity. Make sure it matches validation schema.
   */
  max?: number
  error?: string
  ariaLabel?: string
}

/**
 * The QuantityInput component is a combination of a TextInput and a BaseCheckbox to define quantities.
 * An undefined quantity is meant to be interpreted as unlimited.
 *
 * @example
 * <QuantityInput
 *   label="Quantity"
 *   name="quantity"
 *   min={0}
 *   onChange={(value) => console.log(value)}
 * />
 */
export const QuantityInput = ({
  label = 'Quantité',
  name = 'quantity',
  onChange,
  onBlur,
  disabled,
  required,
  requiredIndicator,
  min = 0,
  max = 1_000_000,
  value,
  error,
  ariaLabel,
}: QuantityInputProps) => {
  const quantityName = name
  const quantityRef = useRef<HTMLInputElement>(null)

  const unlimitedName = `${name}.unlimited`
  const unlimitedRef = useRef<HTMLInputElement>(null)

  const isEmptyValue = value !== 0 && !value
  const [isUnlimited, setIsUnlimited] = useState(isEmptyValue)

  useEffect(() => {
    // Move focus to the quantity input if unlimited is unchecked.
    const focusedElement = document.activeElement as HTMLElement
    const isUnlimitedCheckboxFocused = focusedElement === unlimitedRef.current
    if (!isUnlimited && isUnlimitedCheckboxFocused) {
      quantityRef.current?.focus()
    }
  }, [isUnlimited])

  useEffect(() => {
    if (isUnlimited !== isEmptyValue) {
      setIsUnlimited(isEmptyValue)
    }
  }, [isEmptyValue])

  const onQuantityChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.value && /[,.]/.test(event.target.value)) {
      event.target.value = event.target.value.split('.')[0].split(',')[0]
    }
    onChange?.(event)

    setIsUnlimited(event.target.value === '')
  }

  const onCheckboxChange = () => {
    let nextFieldValue = `${min}`
    if (!isUnlimited) {
      // If the checkbox is going to be checked,
      // we need to clear the quantity field as an empty
      // string means unlimited quantity.
      nextFieldValue = ''
    }

    onChange?.({
      target: { value: nextFieldValue },
    } as React.ChangeEvent<HTMLInputElement>)

    if (quantityRef.current) {
      quantityRef.current.value = nextFieldValue
    }

    setIsUnlimited((unlimited) => !unlimited)
  }

  const inputExtension = (
    <Checkbox
      ref={unlimitedRef}
      label="Illimité"
      name={unlimitedName}
      onChange={onCheckboxChange}
      checked={isUnlimited}
      disabled={disabled}
    />
  )

  return (
    <TextInput
      ref={quantityRef}
      name={quantityName}
      label={label}
      required={required}
      requiredIndicator={requiredIndicator}
      disabled={disabled}
      type="number"
      min={min}
      max={max}
      step={1}
      extension={inputExtension}
      onChange={onQuantityChange}
      onBlur={onBlur}
      value={isUnlimited ? '' : (value?.toString() ?? '')}
      error={error}
      aria-label={ariaLabel}
    />
  )
}
